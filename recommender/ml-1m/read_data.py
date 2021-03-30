import pandas as pd

uname = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table(r'users.dat', sep='::', header=None, names=uname, engine='python')
rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
ratings = pd.read_table(r'ratings.dat', sep='::', header=None, names=rnames, engine='python')
mname = ['movie_id', 'title', 'genres']
movies = pd.read_table(r'movies.dat', sep='::', header=None, names=mname, engine='python')

data = pd.merge(pd.merge(movies, ratings), users)
print(data)
