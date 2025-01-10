import json
import os

import aiofiles
import folium

from app.config.read_config import UPLOAD_FOLDER
from folium.folium import Map
from folium.map import Marker, Icon, LayerControl
from folium.features import GeoJson
from folium.plugins import Draw
from ipinfo import getHandlerAsync
from shapely import Polygon, Point
from app.config.read_config import ACCESS_TOKEN_IPINFO
from app.utils.github_api import get_info_war
from flask import current_app, flash
from shapely.geometry import shape
from shapely.errors import TopologicalError


async def iframe_map(
        user_ip: str,
        draw: bool = False
):
    geojson_data = await get_info_war(
        repo_link="cyterat/deepstate-map-data",
        repo_path="data"
    )
    if geojson_data[0] is False:
        with current_app.app_context():
            flash(
                message='Ми не змогли знайти інформацію про тимчасово окуповані території України',
                category='danger'
            )

    handler = getHandlerAsync(ACCESS_TOKEN_IPINFO)
    details = await handler.getDetails(ip_address=user_ip)
    try:
        latitude, longitude = details.latitude, details.longitude
        folium_map = Map(
            location=[latitude, longitude],
            zoom_start=6
        )
        Marker(
            location=[details.latitude, details.longitude],
            tooltip="Ваше місцезнаходження",
            icon=Icon(color="green")
        ).add_to(folium_map)

        coordinates = geojson_data[1].get('features')[0].get('geometry').get('coordinates')
        polygon = [Polygon(coordinate) for coordinate_set in coordinates for coordinate in coordinate_set][0]
        marker_point = Point(latitude, longitude)

        if polygon.contains(marker_point):
            with current_app.app_context():
                flash(
                    message='Ви у небезпечній зоні! Будьте обережні!',
                    category='danger'
                )
        else:
            with current_app.app_context():
                flash(
                    message='Ви не знаходитесь у небезпечній зоні!',
                    category='success'
                )
    except AttributeError:
        flash(
            message='Ми не змогли знайти інформацію про ваше місцезнаходження',
            category='danger'
        )
        folium_map = Map()
    folium_map.get_root().height = "94%"

    GeoJson(
        geojson_data[1],
        name="Тимчасово окуповані території України",
        style_function=lambda style: {
            "fillColor": "red",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.6,
        }
    ).add_to(folium_map)
    user_group = folium.FeatureGroup(name="Дані небезпечних територій від наших користувачів")
    all_files = [f for f in os.listdir(UPLOAD_FOLDER) if
                 os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    for file_user in all_files:
        async with aiofiles.open(f"{UPLOAD_FOLDER}{file_user}", mode='r') as file:
            content = await file.read()
        user_geojson = GeoJson(
            content,
            name="Дані небезпечних територій від наших користувачів",
            style_function=lambda style: {
                "fillColor": "red",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.6,
            }
        )
        user_group.add_child(user_geojson)
    folium_map.add_child(user_group)

    if draw:
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

    LayerControl().add_to(folium_map)
    iframe = folium_map.get_root()._repr_html_()
    return [200, iframe]


async def validate_geojson_with_schema(geojson_data):
    try:
        geojson_data = json.loads(geojson_data)
        for feature in geojson_data['features']:
            geometry = shape(feature['geometry'])
            if not geometry.is_valid:
                return [False, geojson_data]
        return [True, geojson_data]
    except TopologicalError as error:
        return [False, error]
    except json.JSONDecodeError as error:
        return [False, error]
