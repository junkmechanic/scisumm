import pickle
from Config import DIR
#from process_tree import Node

pos = {}
neg = {}
pos['right'] = 0
pos['wrong'] = 0
neg['right'] = 0
neg['wrong'] = 0

picklefile = DIR['DATA'] + 'test-sentences-pickle'
with open(picklefile, 'rb') as pfile:
    global data
    data = pickle.load(pfile)

for key in data.keys():
    real = data[key]['reallbl']
    pred = data[key]['svmval']
    if real == '+1':
        if pred > 0:
            pos['right'] += 1
        else:
            pos['wrong'] += 1
    elif real == '-1':
        if pred < 0:
            neg['right'] += 1
        else:
            neg['wrong'] += 1
    else:
        print "Label was not correctly assigned."

print "Positive Samples Classified Correctly : " + str(pos['right'])
print "Positive Samples Classified Incorrectly : " + str(pos['wrong'])
print "Negative Samples Classified Correctly : " + str(neg['right'])
print "Negative Samples Classified Incorrectly : " + str(neg['wrong'])
