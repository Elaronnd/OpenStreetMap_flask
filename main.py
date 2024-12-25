from typing import Optional
import os
import folium
from flask import Flask, render_template, abort, redirect, request
from forms import UserForm
from secrets import token_bytes

locs = []
m = folium.Map()
app = Flask(__name__)
# app.config['SECRET_KEY'] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///mapdb.db'


@app.route('/', methods=["GET", "POST"])
def index_reg_or_log():
    form = UserForm()
    if request.method == "GET":
        return render_template("index_reg_or_log.html", Title="Register", form=form)


@app.route('/main-map')
def show_user_map():
    if os.path.exists('templates/map.html'):
        return render_template('map.html')
    else:
        abort(404)


@app.route('/get-cords/x-cord=<x>&y-cord=<y>')
def get_cords(x: float, y: float) -> Optional[render_template]:
    try:
        if [x, y] not in locs:
            locs.append([x, y])
        for loc in locs:
            print(loc)
            folium.Marker(
                location=[float(loc[0]), float(loc[1])],
                tooltip="Click me!",
                icon=folium.Icon(color="green"),).add_to(m)
        m.save("templates/map.html")
    finally:
        return redirect("/main-map")


if __name__ == "__main__":
    app.run(debug=True)
