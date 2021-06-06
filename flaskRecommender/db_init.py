from flaskRecommender import db, bcrypt
from flaskRecommender.models import Movie, User
from recommender.read_movies import get_movies

'''
This script initialises the database and create an admin account for the application
'''

db.create_all()
# insert all the movies to the database
for movie_id, movie_name in get_movies():
    movie = Movie(id=movie_id, name=movie_name)
    db.session.add(movie)

# create an admin account
hashed_password = bcrypt.generate_password_hash('test').decode('utf8')
test_user = User(username='test', email='test@test.com', password=hashed_password, gender='M', age=18, occupation=4)
db.session.add(test_user)

db.session.commit()
