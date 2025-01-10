from app.web.routes import app
from app.models import User, Draws, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(
        debug=True,
        host="0.0.0.0",
        port=80
    )
