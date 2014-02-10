import pickle
from Config import DIR
#from process_tree import Node


picklefile = DIR['DATA'] + 'test-sentences-pickle'
with open(picklefile, 'rb') as pfile:
    global data
    data = pickle.load(pfile)
print(data['W06-3312-216'])
