# choose movie from database
import pandas as pd
import requests
import os

mname = ['movie_id', 'title', 'genres']

data_dir = os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m')

def get_movie_details(movie_name):
    movie_info = dict()
    movie_info['movie_name'] = movie_name[:-6]
    movie_info['movie_year'] = movie_name[-5:-1]
    name = movie_name[:-6]
    year = movie_name[-5:-1]
    # use omdbapi to get the movie detail
    url = 'http://www.omdbapi.com/?i=tt3896198&apikey=c9afa68e&t={}&y={}'.format(name,year)
    movie_data = requests.get(url=url).json()
    if 'Poster' in movie_data:
        movie_info['Poster'] = movie_data['Poster']
    if 'imdbID' in movie_data:
        movie_info['imdbID'] = movie_data['imdbID']
    return movie_info


def replace_the(movie):
    """
    fix the typo in the movielens data
    :return fixed movie name
    """
    if ', The' in movie:
        movie = movie.replace(', The', '')
        movie = 'The ' + movie
    return movie


def get_movie(index):

    indexs = [2858,  260, 1196, 1210,  480, 2028,  589, 2571, 1270,  593, 1580,
            1198,  608, 2762,  110, 2396, 1197,  527, 1617, 1265, 1097, 2628,
            2997,  318,  858,  356, 2716,  296, 1240,    1, 1214,  457, 2916,
            3578, 1200,  541, 2987, 1259,   50,   34, 2791, 1193, 3175,  780,
             919,  924, 1127, 2355, 1387, 1221,  912, 1036, 1213, 1610,  377,
            1291, 2000, 1136, 3114, 1307, 1704, 1721, 1968,  648, 2599, 3793,
              32, 2174, 2797, 2918, 2291, 3471,  590, 2959, 1374, 1394,  592,
            2683, 1784, 1304, 3418, 1573,  223,  380, 2706, 1225, 1584, 1527,
            3481,  750, 1923, 2699,   39,   21, 2804, 1393,  588, 2406, 1220,
             733]
    movies = pd.read_table(os.path.join(data_dir, 'movies.dat'), sep='::', header=None, names=mname, engine='python')
    movies.title = movies.title.apply(replace_the)
    ran_movie = movies[movies['movie_id']==indexs[index]]
    movie_name = str(ran_movie['title'].values[0])

    movie_info = get_movie_details(movie_name)
    movie_info['movie_id'] = int(ran_movie['movie_id'])
    movie_info['movie_genres'] = ran_movie['genres'].values[0].split('|')

    return movie_info

def get_random_movie():
    """
    randomly get the movie from the movie data

    """
    movies = pd.read_table(os.path.join(data_dir, 'movies.dat'), sep='::', header=None, names=mname, engine='python')
    movies.title = movies.title.apply(replace_the)
    ran_movie = movies.sample()
    movie_name = str(ran_movie['title'].values[0])
    movie_info = get_movie_details(movie_name)
    movie_info['movie_id'] = int(ran_movie['movie_id'])
    movie_info['movie_genres'] = ran_movie['genres'].values[0].split('|')

    return movie_info

def get_movies():

    movies = pd.read_table(os.path.join(data_dir, 'movies.dat'), sep='::', header=None, names=mname, engine='python')
    movies.title = movies.title.apply(replace_the)
    return movies[['movie_id', 'title']].values
