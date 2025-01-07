from flask import Flask, request, jsonify, abort, Response, render_template
from app.utils.map_generator import iframe_map

app = Flask(__name__)

@app.errorhandler(400)
async def page_not_found(e):
    return jsonify("error", e)

@app.route("/")
async def fullscreen():
    iframe = await iframe_map(request.remote_addr)
    if iframe[0] != 200:
        return abort(Response(iframe[1], iframe[0]))
    return render_template(
        template_name_or_list="index.html",
        iframe=iframe[1],
    )
