from models import db, User
from main import app


db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.add(User(username='guest', email='guest@example.com', password="81962e2jh88"))
    db.session.commit()
    db.session.close()
