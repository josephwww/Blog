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
    url = 'http://www.omdbapi.com/?i=tt3896198&apikey=c9afa68e&t={}&y={}'.format(name,year)
    movie_data = requests.get(url=url).json()
    if 'Poster' in movie_data:
        movie_info['Poster'] = movie_data['Poster']
    if 'imdbID' in movie_data:
        movie_info['imdbID'] = movie_data['imdbID']
    return movie_info


def replace_the(movie):
    if ', The' in movie:
        movie = movie.replace(', The', '')
        movie = 'The ' + movie
    return movie


def get_movie():
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
