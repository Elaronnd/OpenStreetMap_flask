from os import urandom
from flask import Flask, request, jsonify, abort, Response, render_template, flash, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from app.forms import UserLoginForm, UserRegForm
from app.models import User, db
from flask_bcrypt import Bcrypt
from app.utils.map_generator import iframe_map

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safemap.db'
app.config['SECRET_KEY'] = urandom(16)
# maybe better to make secret key in .env file (?)
# idk, maybe... but not .env since we have yaml
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
    if current_user.is_authenticated:
        return redirect("/")
    elif request.method == "GET":
        return render_template("reg.html", form=UserRegForm())
    elif request.method == "POST":
        form = UserRegForm()
        if form.validate_on_submit():
            username = form.username.data.lower()
            email = form.email.data.lower()
            password = bcrypt.generate_password_hash(form.password.data.lower()).decode('utf-8')
            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                flash("Пошта вже зареєстрована")
                return render_template("reg.html", form=UserRegForm())
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(message="Реєстрація пройшла успішно!", category="success")
            return redirect("/")

        else:
            return render_template("reg.html", form=UserRegForm())


@app.route('/login', methods=["GET", "POST"])
async def login():
    if current_user.is_authenticated:
        return redirect("/")
    elif request.method == "GET":
        return render_template("log.html", form=UserLoginForm())
    elif request.method == "POST":
        form = UserLoginForm()
        if form.validate_on_submit():
            username = form.username.data.lower()
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data.lower()):
                login_user(user)
                return redirect("/")
            else:
                flash("Неправильний логін або пароль")
                return render_template("log.html", form=UserLoginForm())
        return render_template("log.html", form=UserLoginForm())


@app.route("/profile")
@login_required
async def profile():
    return render_template("profile.html", current_user=current_user)


@app.route('/logout', methods=["POST"])
@login_required
async def logout():
    logout_user()
    return redirect("/")


@app.route("/draw")
async def draw():
    iframe = await iframe_map(
        request.remote_addr,
        draw=True
    )
    if iframe[0] != 200:
        return abort(Response(iframe[1], iframe[0]))
    return render_template(
        "index.html",
        iframe=iframe[1],
        current_user=current_user,
        fixed_top=True
    )


@app.route("/")
async def index():
    iframe = await iframe_map(request.remote_addr)
    if iframe[0] != 200:
        return abort(Response(iframe[1], iframe[0]))
    return render_template(
        template_name_or_list="index.html",
        iframe=iframe[1],
        current_user=current_user,
        fixed_top=True
    )
