import pickle
import pandas as pd


# generate the movie_id to index in the rating matrix
uname = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table(r'users.dat', sep='::', header=None, names=uname, engine='python')
users.to_pickle('users.pkl')
rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
ratings = pd.read_table(r'ratings.dat', sep='::', header=None, names=rnames, engine='python')
rating_matrix = ratings.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
movie_to_index = {v: k for k, v in enumerate(rating_matrix.columns)}

# Store data (serialize)
with open('movie_to_index.pkl', 'wb') as handle:
    pickle.dump(movie_to_index, handle, protocol=pickle.HIGHEST_PROTOCOL)
rating_matrix.to_pickle('rating_matrix.pkl')