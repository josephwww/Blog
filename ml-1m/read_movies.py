import pandas as pd
import secrets

mname = ['movie_id', 'title', 'genres']
movies = pd.read_table(r'movies.dat', sep='::', header=None, names=mname, engine='python')

ran_movie = secrets.choice(movies.title.values)