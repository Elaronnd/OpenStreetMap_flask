from os import urandom
from flask import Flask, request, jsonify, abort, Response, render_template, flash, redirect, url_for
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from app.forms import UserLoginForm, UserRegForm, ChangePasswordForm, NewPasswordForm
from app.models import User, db
from flask_bcrypt import Bcrypt
from app.utils.map_generator import iframe_map
from app.utils import send_checker_message
from cryptography.fernet import Fernet


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safemap.db'
app.config['SECRET_KEY'] = urandom(16)
# maybe better to make secret key in .env file (?)
# idk, maybe... but not .env since we have yaml
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
key = Fernet.generate_key()
fernet = Fernet(key)


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
            print(user.password)
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


@app.route('/settings')
@login_required
async def settings():
    return render_template('settings.html', current_user=current_user)


@app.route('/change-password', methods=["GET", "POST"])
@login_required
async def change_password():
    changeform = ChangePasswordForm()
    if request.method == "GET":
        return render_template('email_checker.html', form=changeform)
    elif request.method == "POST":
        if changeform.validate_on_submit():
            username = changeform.username.data.lower()
            user = User.query.filter_by(username=username).first()
            email = changeform.email.data.lower()
            token = fernet.encrypt(f"{username}:{email}".encode())
            if user and user.email == email:
                msg = url_for('change_password_link', token=token.decode()
                              )
                # fernet.encrypt(data=bytes((changeform.new_password.data).encode()))
                send_checker_message.send_msg(imsg=request.host + msg, email=email)
                flash(message=f"Надіслано повідомлення на адресс {email}", category="success")
                return redirect("/")
            else:
                flash(f"Не вдалося!")
                return redirect("/")


@app.route('/change-password-link/token=<token>', methods=["GET", "POST"])
async def change_password_link(token):
    decrypted_token = fernet.decrypt(token).decode()
    username, email = decrypted_token.split(':')
    user = User.query.filter_by(username=username).first()
    form = NewPasswordForm()
    if request.method == "GET":
        return render_template("new_password.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            if user and user.email == email:
                password = form.new_password.data.lower()
                user.password = bcrypt.generate_password_hash(password=password).decode('utf-8')
                db.session.commit()
                return redirect('/')


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
