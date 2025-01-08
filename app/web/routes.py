from os import urandom
import flask
from flask import Flask, request, jsonify, abort, Response, render_template, flash, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from app.forms import UserLoginForm, UserRegForm
from app.models import User, db
from flask_bcrypt import Bcrypt

# from app.utils.map_generator import iframe_map

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safemap.db'
app.config['SECRET_KEY'] = urandom(16)
# maybe better to make secret key in .env file (?)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.errorhandler(400)
async def page_not_found(e):
    return jsonify("error", e)


@app.route('/register', methods=["GET", "POST"])
async def register():
    if request.method == "GET":
        return render_template("reg.html", form=UserRegForm())
    elif request.method == "POST":
        form = UserRegForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                return "Email is already in use."
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            flash("Регистрация прошла успешно!")
            return redirect("/")

        else:
            return render_template("reg.html", form=UserRegForm())


@app.route('/login', methods=["GET", "POST"])
async def login():
    if request.method == "GET":
        return render_template("log.html", form=UserLoginForm())
    elif request.method == "POST":
        form = UserLoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/")
            else:
                return render_template("log.html", form=UserLoginForm())


@app.route('/logout')
@login_required
async def logout():
    logout_user()
    return redirect("/")


@app.route("/")
async def fullscreen():
    return render_template("base.html")
    # iframe = await iframe_map(request.remote_addr)
    # if iframe[0] != 200:
    #     return abort(Response(iframe[1], iframe[0]))
    # return render_template(
    #     template_name_or_list="index.html",
    #     iframe=iframe[1],
    # )
