from folium.folium import Map
from folium.map import Marker, Icon, LayerControl
from folium.features import GeoJson
from ipinfo import getHandlerAsync
from app.config.read_config import ACCESS_TOKEN_IPINFO
from app.utils.github_api import get_info_war


# async def iframe_map(
#         user_ip: str
# ):
#     handler = getHandlerAsync(ACCESS_TOKEN_IPINFO)
#     details = await handler.getDetails(user_ip)
#     try:
#         map = Map(
#             location=[details.latitude, details.longitude],
#             zoom_start=6
#         )
#         Marker(
#             location=[details.latitude, details.longitude],
#             tooltip="Твоє місцезнаходження",
#             icon=Icon(color="green")
#         ).add_to(map)
#     except AttributeError:
#         return [400, "you entered to page by local ip, please entered by wan ip\n{details.all}"]
#     map.get_root().height = "100%"
#     geojson_data = await get_info_war(
#         repo_link="cyterat/deepstate-map-data",
#         repo_path="data"
#     )
#     if geojson_data[0] is False:
#         pass # Зробити повідомлення по типу: "Ми не змогли знайти інформацію про тимчасово окуповані території України"
#
#     GeoJson(
#         geojson_data[1],
#         name="Тимчасово окуповані території України",
#         style_function=lambda feature: {
#             "fillColor": "red",
#             "color": "black",
#             "weight": 1,
#             "fillOpacity": 0.6,
#         }
#     ).add_to(map)
#
#     LayerControl().add_to(map)
#     iframe = map.get_root()._repr_html_()
#     return [200, iframe]
