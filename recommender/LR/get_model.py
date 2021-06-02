from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit
import pandas as pd
import os
import pickle

rating_matrix = pd.read_pickle(os.path.join('..', 'ml-1m', 'rating_matrix.pkl')).astype(int)
users = pd.read_pickle(os.path.join('..', 'ml-1m', 'users.pkl'))

users.set_index(users.user_id, inplace=True)

X = rating_matrix.values
y = users.gender.to_numpy()

models=[]
scores=[]
for train_ids, test_ids in ShuffleSplit(n_splits=1, test_size=0.2, random_state=20210511).split(X):
    x_train, x_test = X[train_ids], X[test_ids]
    y_train, y_test = y[train_ids], y[test_ids]
    model = LogisticRegression(solver='liblinear', C=0.05)
    model.fit(x_train, y_train)
    models.append(model)
    scores.append(model.score(x_test, y_test))

best_gender_model = models[max(enumerate(scores), key=lambda x:x[1])[0]]
print(max(enumerate(scores), key=lambda x:x[1]))
filename = 'LR_gender.pkl'
#pickle.dump(best_gender_model, open(filename, 'wb'))


y = users.age.to_numpy()
models=[]
scores=[]
for train_ids, test_ids in ShuffleSplit(n_splits=1, test_size=0.2, random_state=20210511).split(X):
    x_train, x_test = X[train_ids], X[test_ids]
    y_train, y_test = y[train_ids], y[test_ids]
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', C=0.05, max_iter=4000)
    model.fit(x_train, y_train)
    models.append(model)
    scores.append(model.score(x_test, y_test))

best_age_model = models[max(enumerate(scores), key=lambda x:x[1])[0]]
print(max(enumerate(scores), key=lambda x:x[1]))
filename = 'LR_age.pkl'
#pickle.dump(best_age_model, open(filename, 'wb'))

y = users.occupation.to_numpy()
models=[]
scores=[]
for train_ids, test_ids in ShuffleSplit(n_splits=1, test_size=0.2, random_state=20210511).split(X):
    x_train, x_test = X[train_ids], X[test_ids]
    y_train, y_test = y[train_ids], y[test_ids]
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', C=0.05, max_iter=4000)
    model.fit(x_train, y_train)
    models.append(model)
    scores.append(model.score(x_test, y_test))

best_occupation_model = models[max(enumerate(scores), key=lambda x:x[1])[0]]
print(max(enumerate(scores), key=lambda x:x[1]))
filename = 'LR_occupation.pkl'
#pickle.dump(best_occupation_model, open(filename, 'wb'))