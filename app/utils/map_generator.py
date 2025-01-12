from json import loads
from json.decoder import JSONDecodeError
from os import listdir, path
from aiofiles import open
from folium.folium import Map
from shapely.geometry.geo import shape
from app.config.read_config import UPLOAD_FOLDER, ACCESS_TOKEN_IPINFO
from folium.map import Marker, Icon, LayerControl, FeatureGroup
from folium.features import GeoJson
from folium.plugins import Draw
from ipinfo import getHandlerAsync
from shapely.geometry import Polygon, Point
from shapely.errors import TopologicalError
from flask import current_app, flash
from app.utils.github_api import get_info_war


class DangerZoneMap:
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER
        self.access_token = ACCESS_TOKEN_IPINFO

    async def get_user_location(self, user_ip: str) -> tuple:
        handler = getHandlerAsync(self.access_token)
        details = await handler.getDetails(ip_address=user_ip)
        return details.latitude, details.longitude

    async def process_user_files(self, marker_point: Point) -> list:
        all_files = [f for f in listdir(self.upload_folder) if path.isfile(path.join(self.upload_folder, f))]
        users_data = []
        is_danger = False
        for file_user in all_files:
            async with open(f"{self.upload_folder}/{file_user}", mode='r') as file:
                content = await file.read()
            user_data = loads(content)
            users_data.append(user_data)
            for feature in user_data.get('features'):
                in_danger_zone = await self.check_danger_zone(
                    marker_point=marker_point,
                    geojson_data=feature,
                    coordinates=feature.get('geometry').get('coordinates')
                )
                if in_danger_zone[1] is True:
                    is_danger = True
        return [is_danger, users_data]

    @staticmethod
    async def add_draw_plugin(folium_map: Map):
        Draw(
            export=True,
            draw_options={
                "polyline": False,
                "polygon": True,
                "circle": False,
                "rectangle": False,
                "marker": False,
                "circlemarker": False
            },
            edit_options={"edit": True, "remove": True}
        ).add_to(folium_map)

    @staticmethod
    async def check_danger_zone(marker_point: Point, geojson_data: dict, coordinates: list = None) -> list:
        if not coordinates:
            coordinates = geojson_data.get('features')[0].get('geometry').get('coordinates')
            polygon = [Polygon(coordinate) for coordinate_set in coordinates for coordinate in coordinate_set][0]
        else:
            polygon = Polygon(coordinates[0])
        if polygon.contains(marker_point):
            return [True, marker_point]
        return [False, marker_point]


async def iframe_map(user_ip: str, draw: bool = False):
    danger_zone_map = DangerZoneMap()

    if draw:
        folium_map = Map()
        await danger_zone_map.add_draw_plugin(folium_map)
        LayerControl().add_to(folium_map)

        folium_map.get_root().height = "94%"
        iframe = folium_map.get_root()._repr_html_()
        return [200, iframe]

    latitude, longitude = await danger_zone_map.get_user_location(user_ip)
    marker_point = Point(longitude, latitude)
    folium_map = Map(location=[latitude, longitude], zoom_start=6)

    Marker(
        [latitude, longitude],
        tooltip="Ваше місцезнаходження",
        icon=Icon(color="green")
    ).add_to(folium_map)

    user_group = FeatureGroup(name="Дані небезпечних територій від наших користувачів")
    user_in_danger = await danger_zone_map.process_user_files(marker_point)

    geojson_data = await get_info_war(repo_link="cyterat/deepstate-map-data", repo_path="data")
    if geojson_data[0]:
        GeoJson(
            geojson_data[1],
            name="Тимчасово окуповані території України",
            style_function=lambda _: {
                "fillColor": "red",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.6,
            }
        ).add_to(folium_map)
        in_danger_zone = await danger_zone_map.check_danger_zone(marker_point, geojson_data[1])
        if in_danger_zone[0] or user_in_danger[0]:
            with current_app.app_context():
                flash('Ви у небезпечній зоні! Будьте обережні!', 'danger')
        else:
            with current_app.app_context():
                flash('Ви не знаходитесь у небезпечній зоні!', 'danger')
    else:
        with current_app.app_context():
            flash('Ми не змогли знайти інформацію про тимчасово окуповані території України', 'danger')

    for user_data in user_in_danger[1]:
        GeoJson(user_data,
                style_function=lambda _: {
                    "fillColor": "orange",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.6,
                }
                ).add_to(user_group)

    folium_map.add_child(user_group)

    LayerControl().add_to(folium_map)

    folium_map.get_root().height = "94%"
    iframe = folium_map.get_root()._repr_html_()
    return [200, iframe]


async def validate_geojson_with_schema(geojson_data):
    try:
        geojson_data = loads(geojson_data)
        for feature in geojson_data.get('features'):
            geometry = shape(feature.get('geometry'))
            if not geometry.is_valid:
                return [False, geojson_data]
        return [True, geojson_data]
    except TopologicalError as error:
        return [False, error]
    except JSONDecodeError as error:
        return [False, error]
