import pandas as pd
from scipy.stats import entropy

# get the rating matrix from pickle file
rating_matrix = pd.read_pickle('../ml-1m/rating_matrix.pkl').astype(int)

# calculate the entropy for each movie
movie_entropy = rating_matrix.apply(entropy, base=2, axis=0)

# calculate the popularity for each movie
pop = rating_matrix.astype(bool).sum(axis=0)

# multiply popularity and entropy and get top 100's movies index
movie_index = movie_entropy.multiply(pop).nlargest(100).index
print(movie_index)