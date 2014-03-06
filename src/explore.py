import pickle
from Config import DIR
#from process_tree import Node

pos = {'right': 0, 'wrong': 0}
neg = {'right': 0, 'wrong': 0}

picklefile = DIR['DATA'] + 'test-sentences-pickle'
with open(picklefile, 'rb') as pfile:
    global data
    data = pickle.load(pfile)


def confusion_matrix():
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


def feature_analysis():
    features = r'([\+-]1)\s(.*)'
    for key in data.keys():


def display(real=1, pred=1):
    for key in data.keys():
        if int(data[key]['reallbl']) == real:
            prediction = -1 if data[key]['svmval'] < 0 else +1
            if prediction == pred:
                yield data[key]


def list_sentences(real=1, pred=1):
    for sent in display(real, pred):
        print sent['contextpre']
        print "---Main sentence start-----"
        print sent['sentence']
        print "---Main sentence end-----"
        print sent['contextpos']
        raw_input()


if __name__ == '__main__':
    confusion_matrix()
