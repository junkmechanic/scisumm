import pickle
from Config import DIR
from random import choice


picklefile = DIR['DATA'] + 'test-sentences-pickle'
with open(picklefile, 'rb') as pfile:
    global data
    data = pickle.load(pfile)

bucket = data.keys()
for i in range(10):
    train_set = bucket
    test_set = []
    for k in range(7):
        curr = choice(train_set)
        test_set.append(curr)
        train_set.remove(curr)
