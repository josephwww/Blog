from datetime import datetime
from flaskRecommender import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    ratings = db.relationship('Rating', backref='author', lazy='dynamic')
    demographics = db.relationship('Demography', backref='owner', lazy='dynamic')
    # ratings = db.relationship('Rating', backref='rates', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    date_rated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    film_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # TODO demographic data after voting

    def __repr__(self):
        return f"Rating('{self.film_id}', '{self.score}')"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

    def __repr__(self):
        return f"Movie('{self.name}')"


class Demography(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    male = db.Column(db.Integer, nullable=False, default=0)
    age1 = db.Column(db.Integer, nullable=False, default=0)
    age1_p = db.Column(db.Integer, nullable=False, default=0)
    age2 = db.Column(db.Integer, nullable=False, default=0)
    age2_p = db.Column(db.Integer, nullable=False, default=0)
    occup1 = db.Column(db.Integer, nullable=False, default=0)
    occup1_p = db.Column(db.Integer, nullable=False, default=0)
    occup2 = db.Column(db.Integer, nullable=False, default=0)
    occup2_p = db.Column(db.Integer, nullable=False, default=0)
    date_generated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Demography('{self.male}', '{self.age1}', '{self.age1_p}', '{self.age2}', '{self.age2_p}'\
        , '{self.occup1}', '{self.occup1_p}', '{self.occup2}', '{self.occup2_p}') "
