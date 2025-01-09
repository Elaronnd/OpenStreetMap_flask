from folium.folium import Map
from folium.map import Marker, Icon, LayerControl
from folium.features import GeoJson
from folium.plugins import Draw
from ipinfo import getHandlerAsync
from app.config.read_config import ACCESS_TOKEN_IPINFO
from app.utils.github_api import get_info_war
from flask import current_app, flash


async def iframe_map(
        user_ip: str,
        draw: bool = False
):
    # handler = getHandlerAsync(ACCESS_TOKEN_IPINFO)
    # details = await handler.getDetails(ip_address=user_ip)
    # try:
    #     folium_map = Map(
    #         location=[details.latitude, details.longitude],
    #         zoom_start=6
    #     )
    #     Marker(
    #         location=[details.latitude, details.longitude],
    #         tooltip="Ваше місцезнаходження",
    #         icon=Icon(color="green")
    #     ).add_to(folium_map)
    # except AttributeError:
    #     flash(
    #         message='Ми не змогли знайти інформацію про ваше місцезнаходження',
    #         category='danger'
    #     )
    folium_map = Map()
    folium_map.get_root().height = "94%"
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

    if draw:
        Draw(
            export=True,
            draw_options={
                "polyline": True,
                "polygon": False,
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
