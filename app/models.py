from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250))
    email = db.Column(db.String(250))
    password = db.Column(db.String(250))

    @staticmethod
    def get(user_id):
        return db.get_or_404(User, ident=user_id)



