import os

import pandas as pd
from scipy.spatial.distance import cosine
import pickle


def get_from_rating_space(new_user):
    '''
    from given rating space, use the cosine similarity to find the similar user
    return the top K users demographic
    '''
    K = 10
    rating_matrix = pd.read_pickle(os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m', 'rating_matrix.pkl'))
    handle = open(os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m', 'movie_to_index.pkl'), 'rb')
    movie_to_index = pickle.load(handle)
    handle.close()

    new_user_rating = [0.0] * 3706

    for movie_id, rating in new_user:
        if movie_id not in movie_to_index:
            # this movie has not been voted in rating matrix
            continue
        new_user_rating[movie_to_index[movie_id]] = rating
    new_user = pd.Series(new_user_rating)
    match_users = rating_matrix.apply(lambda x: 1-cosine(x, new_user), axis=1).nlargest(n=K, keep='all') # get the top K users' ID
    users = pd.read_pickle(os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m', 'users.pkl'))

    ages = []
    occupations = []
    genders = []
    for i in match_users.index:
        user = users.iloc[i - 1]
        ages.append(int(user['age']))
        occupations.append(int(user['occupation']))
        genders.append(user['gender'])

    def get_result(*results):
        out = []
        for result in results:
            result_dict = {}
            for value in result:
                if value in result_dict:
                    result_dict[value] += 1
                else:
                    result_dict[value] = 1
            out.extend(sorted(result_dict.items(), key=lambda x: x[1], reverse=True)[:2])
        return out

    return get_result(ages, occupations, genders)
