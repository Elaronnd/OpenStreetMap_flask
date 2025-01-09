from app.web.routes import app, db
from app.models import User  # not useless import


async def first_start():
    with app.app_context():
        db.init_app(app)
        db.create_all()
