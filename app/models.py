from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

    draws = db.relationship('Draws', back_populates='user', lazy=True)

    @staticmethod
    def get(user_id):
        return db.get_or_404(User, ident=user_id)


class Draws(db.Model):
    __tablename__ = "draws"
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='draws')
