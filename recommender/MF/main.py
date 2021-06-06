# user embedding comparison in matrix factorization
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import spatial


# pick one of the available folders
def read_data(path):
    files = {}
    for filename in path.glob('*'):
        if filename.suffix == '.csv':
            files[filename.stem] = pd.read_csv(filename)
        elif filename.suffix == '.dat':
            if filename.stem == 'ratings':
                columns = ['userId', 'movieId', 'rating', 'timestamp']
            elif filename.stem == 'users':
                columns = ['user_id', 'gender', 'age', 'occupation', 'zip']
            else:
                columns = ['movieId', 'title', 'genres']
            data = pd.read_csv(filename, sep='::', names=columns, engine='python')
            files[filename.stem] = data
    return files['ratings'], files['movies'], files['users']

ratings, movies, users = read_data(Path(os.getcwd()))
data = ratings

np.random.seed(3)
msk = np.random.rand(len(data)) < 0.8
train = data[msk].copy()
val = data[~msk].copy()


# The following is a function that encodes a Pandas column as a categorical id.
def proc_col(col, train_col=None):
    """ Encodes a pandas column with continous ids. """
    # Find a unique row, i.e. user or movie
    if train_col is not None:
        uniq = train_col.unique()
    else:
        uniq = col.unique()
    # Maps users/movies to indexes
    name2idx = {o: i for i, o in enumerate(uniq)}
    # And format it and return
    return name2idx, np.array([name2idx.get(x, -1) for x in col]), len(uniq)


# The following is a function that actually converts data into encoding. The proc_col defined above is used.
def encode_data(df, train=None):
    """ Encodes rating data with continous user and movie ids.
    If train is provided, encodes df with the same encoding as train.
    """
    df = df.copy()
    for col_name in ["userId", "movieId"]:
        train_col = None
        if train is not None:
            train_col = train[col_name]
        _, col, _ = proc_col(df[col_name], train_col)
        df[col_name] = col
        df = df[df[col_name] >= 0]
    return df


# test and validation encoding
df_train = encode_data(train)
df_val = encode_data(val, train)

class MatrixFactorization(nn.Module):
    def __init__(self, num_unsers, num_items, emb_size=100):
        super().__init__()
        self.user_emb = nn.Embedding(num_users, emb_size)
        self.item_emb = nn.Embedding(num_items, emb_size)
        #  Initialize embedding using normal distribution
        self.user_emb.weight.data.uniform_(0, 0.05)
        self.item_emb.weight.data.uniform_(0, 0.05)

    def forward(self, u, v):
        u = self.user_emb(u)
        v = self.item_emb(v)
        return (u * v).sum(1)


num_users = len(df_train.userId.unique())
num_items = len(df_train.movieId.unique())

model = MatrixFactorization(num_users, num_items, emb_size=100)

def validation_loss(model, unsqueeze=False):
    model.eval()
    users = torch.LongTensor(df_val.userId.values)
    items = torch.LongTensor(df_val.movieId.values)
    ratings = torch.FoatTensor(df_val.rating.values)
    if unsqueeze:
        ratings = ratings.unsqueeze(1)
    y_hat = model(users, items)
    loss = F.mse_loss(y_hat, ratings)
    print("validation loss {:.3f}".format(loss.item()))

def train_mf(model, epochs=10, lr=0.01, wd=0.0, unsqueeze=False):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    model.train()
    for i in range(epochs):
        users = torch.LongTensor(df_train.userId.values)
        items = torch.LongTensor(df_train.movieId.values)
        ratings = torch.FloatTensor(df_train.rating.values)
        if unsqueeze:
            ratings = ratings.unsqueeze(1)
        y_hat = model(users, items)
        loss = F.mse_loss(y_hat, ratings)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(loss.item())
    validation_loss(model, unsqueeze)
train_mf(model, epochs=10, lr=0.1)

user_embed = model.user_emb(torch.LongTensor([i for i in range(num_users)]))
user_embed = list(map(lambda x: x.detach().numpy(), user_embed))

gender_accu = 0
age_accu = 0
occup_accu = 0
gen_true = []
gen_pred = []
age_true = []
age_pred = []
occu_true = []
occu_pred = []
for i in range(len(user_embed)):
    print(i)
    max_sim = 0
    max_index = i
    for j in range(len(user_embed)):
        if j == i:
            continue
        result = 1 - spatial.distance.cosine(user_embed[i], user_embed[j])
        if result > max_sim:
            max_sim = result
            max_index = j
    if users.iloc[i].gender == users.iloc[max_index].gender:
        gender_accu += 1
    if users.iloc[i].age == users.iloc[max_index].age:
        age_accu += 1
    if users.iloc[i].occupation == users.iloc[max_index].occupation:
        occup_accu += 1
    gen_true.append(users.iloc[i].gender)
    gen_pred.append(users.iloc[max_index].gender)
    age_true.append(users.iloc[i].age)
    age_pred.append(users.iloc[max_index].age)
    occu_true.append(users.iloc[i].occupation)
    occu_pred.append(users.iloc[max_index].occupation)
print(gender_accu, age_accu, occup_accu)

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

y_true = gen_true
y_pred = gen_pred
classes = ['M', 'F']


def plot_confusion_matrix(cm, classes,
                          normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    import itertools
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()


cnf_matrix = confusion_matrix(y_true, y_pred, labels=classes)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=classes,
                      title='gender prediction confusion matrix')

y_true = age_true
y_pred = age_pred

classes = np.unique(y_true)

cnf_matrix = confusion_matrix(y_true, y_pred, labels=classes)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=classes,
                      title='age prediction confusion matrix')

y_true = occu_true
y_pred = occu_pred

classes = np.unique(y_true)

cnf_matrix = confusion_matrix(y_true, y_pred, labels=classes)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure(figsize=(20, 15))


def plot_confusion_matrix(cm, classes,
                          normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    import itertools
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')

plot_confusion_matrix(cnf_matrix, classes=classes,
                      title='occupation prediction confusion matrix')
