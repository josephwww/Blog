# get the demographic prediction for web app

import os
import pandas as pd
from scipy.spatial.distance import cosine
import pickle

def generate_rating_space(new_user):
    '''
    for given new user ratings, it generate the rating vector in Pandas Series

    :param new_user: List of two elements tuples. tuple includes movie index and score.
    :return: the rating vector for given user
    '''
    handle = open(os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m', 'movie_to_index.pkl'), 'rb')
    movie_to_index = pickle.load(handle)
    handle.close()

    # initial the rating vector
    new_user_rating = [0.0] * 3706

    for movie_id, rating in new_user:
        if movie_id not in movie_to_index:
            # this movie has not been voted in rating matrix
            continue
        new_user_rating[movie_to_index[movie_id]] = rating
    return pd.Series(new_user_rating)


def get_from_rating_space(new_user):
    '''
    from given rating space, use the cosine similarity to find the similar user
    return the top K users demographic
    :param new_user: the new user
    '''
    K = 100
    #rating_matrix = pd.read_pickle(os.path.join(os.path.join(os.path.dirname(__file__)), 'ml-1m', 'rating_matrix.pkl'))
    rating_matrix = pd.read_pickle(os.path.join('recommender', 'ml-1m', 'rating_matrix.pkl'))
    new_user = generate_rating_space(new_user)

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

def get_from_LR(new_user):
    new_user = generate_rating_space(new_user).to_numpy()

    gender_LR = pickle.load(open(os.path.join('recommender', 'LR', 'LR_gender.pkl'), 'rb'))
    pred_gender = gender_LR.predict([new_user])[0]

    age_LR = pickle.load(open(os.path.join('recommender', 'LR', 'LR_age.pkl'), 'rb'))
    pred_age = int(age_LR.predict([new_user])[0])

    occupation_LR = pickle.load(open(os.path.join('recommender', 'LR', 'LR_occupation.pkl'), 'rb'))
    pred_occupation = int(occupation_LR.predict([new_user])[0])

    flip_gender = {'M': 'F', 'F': 'M'}
    return (pred_age, 100), (-1, 0), (pred_occupation, 100), (-1, 0), (pred_gender, 100), (flip_gender[pred_gender], 0)