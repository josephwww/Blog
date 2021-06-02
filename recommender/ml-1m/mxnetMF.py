from mxnet.gluon import Block, nn, Trainer
from mxnet.gluon.loss import L2Loss
from mxnet import autograd, ndarray as F
import mxnet as mx

import numpy as np
import random
import logging
import re

__reference__ = 'https://www.endpoint.com/blog/2018/07/17/recommender-mxnet'

from mxnet.tools.bandwidth.measure import logger

class DataIter(mx.io.DataIter):
    def __init__(self, data, batch_size = 16):
        super(DataIter, self).__init__()
        self.batch_size = batch_size
        self.all_user_ids = set()
        self.data = data
        self.index = 0

        for user_id, item_id, _ in data:
            self.all_user_ids.add(user_id)

    @property
    def user_count(self):
        return len(self.all_user_ids)

    @property
    def item_count(self):
        # we just know the value even though 10 of them were
        # not voted
        return 150

    def next(self):
        index = self.index * self.batch_size
        endindex = index + self.batch_size

        if len(self.data) <= index:
            raise StopIteration
        else:
            user_ids = []
            item_ids = []
            ratings = []

            user_ids = self.data[index:endindex, 0]
            item_ids = self.data[index:endindex, 1]
            ratings   = self.data[index:endindex, 2]

            data_all = [mx.nd.array(user_ids), mx.nd.array(item_ids)]
            label_all = [mx.nd.array([r]) for r in ratings]

            self.index += 1

            return mx.io.DataBatch(data_all, label_all)

    def reset(self):
        self.index = 0
        random.shuffle(self.data)

def get_data(batch_size):
    user_ids = []
    item_ids = []
    ratings = []

    with open("ratings.dat", "r") as file:
        for line in file:
            user_id, item_id, rating, _ = line.strip().split("::")

            user_ids.append(int(user_id))
            item_ids.append(int(item_id))
            ratings.append(float(rating) / 10.0)

    all_raw = np.asarray(list(zip(user_ids, item_ids, ratings)), dtype='float32')

    return DataIter(all_raw, batch_size = batch_size)

train = get_data(64)

class Model(Block):
    def __init__(self, k, dataiter, **kwargs):
        super(Model, self).__init__(**kwargs)

        with self.name_scope():
            self.user_embedding = nn.Embedding(input_dim = dataiter.user_count, output_dim=k)
            self.item_embedding = nn.Embedding(input_dim = dataiter.item_count, output_dim=k)

    def forward(self, x):
        user = self.user_embedding(x[0] - 1)
        item = self.item_embedding(x[1] - 1)

        # the following is a dot product in essence
        # summing up of the element-wise multiplication
        pred = user * item
        return F.sum_axis(pred, axis = 1)

context = mx.gpu() if mx.test_utils.list_gpus() else mx.cpu()
model = Model(16, train)
model.collect_params().initialize(mx.init.Xavier(), ctx=context)

# model.load_params("model.mxnet", ctx=context)

def fit(model, train, num_epoch):
    trainer = Trainer(model.collect_params(), 'adam')

    for epoch_id in range(num_epoch):
        print(f'epoch {epoch_id}')
        batch_id = 0
        train.reset()

        for batch in train:
            with autograd.record():
                targets = F.concat(*batch.label, dim=0)
                predictions = model(batch.data)
                L = L2Loss()
                loss = L(predictions, targets)
                loss.backward()

            trainer.step(batch.data[0].shape[0])

            if (batch_id + 1) % 1000 == 0:
                mean_loss = F.mean(loss).asnumpy()[0]
                logger.info(f'Epoch {epoch_id + 1} / {num_epoch} | Batch {batch_id + 1} | Mean Loss: {mean_loss}')

            batch_id += 1

    logger.info('Saving model parameters')
    model.save_parameters("model.mxnet")

fit(model, train, num_epoch=10)
user_embed = model.collect_params().get('embedding0_weight').data()
movie_embed = model.collect_params().get('embedding1_weight').data()

import pandas as pd

uname = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table(r'users.dat', sep='::', header=None, names=uname, engine='python')
gender_accu = 0
age_accu = 0
occup_accu = 0
for i in range(len(user_embed)):
    print(i)
    max_sim = 0
    max_index = i
    for j in range(len(user_embed)):
        if j == i:
            continue
        result = 1 - spatial.distance.cosine(user_embed[i].asnumpy(), user_embed[j].asnumpy())
        if result > max_sim:
            max_sim = result
            max_index = j
    if users.iloc[i].gender == users.iloc[max_index].gender:
        gender_accu += 1

    if users.iloc[i].age == users.iloc[max_index].age:
        age_accu += 1
    if users.iloc[i].occupation == users.iloc[max_index].occupation:
        occup_accu += 1
print(gender_accu, age_accu, occup_accu)