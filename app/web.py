from flask import Flask, request, jsonify, abort, Response
from ipinfo import getHandler
from app.config.read_config import ACCESS_TOKEN
import folium

app = Flask(__name__)

@app.errorhandler(400)
def page_not_found(e):
    return jsonify("error", e)

@app.route("/")
def fullscreen():
    handler = getHandler(ACCESS_TOKEN)
    details = handler.getDetails(request.remote_addr)
    m = folium.Map()
    try:
        folium.Marker(
            location=[details.latitude, details.longitude],
            tooltip=details.all,
            icon=folium.Icon(color="green")
        ).add_to(m)
    except AttributeError:
        return abort(Response(f"you entered to page by local ip, please entered by wan ip\n{details.all}", 400))
    return m.get_root().render()


