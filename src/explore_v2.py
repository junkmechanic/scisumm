import re
import pickle
from Config import DIR
import matplotlib.pyplot as plt
#from process_tree import Node

pos = {'right': 0, 'wrong': 0, 'rightkeys': [], 'wrongkeys': []}
neg = {'right': 0, 'wrong': 0, 'rightkeys': [], 'wrongkeys': []}
verb, subj, obj = [], [], []
featurelist = {}

picklefile = DIR['DATA'] + 'test-sentences-pickle1'
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
                pos['rightkeys'].append(key)
            else:
                pos['wrong'] += 1
                pos['wrongkeys'].append(key)
        elif real == '-1':
            if pred < 0:
                neg['right'] += 1
                neg['rightkeys'].append(key)
            else:
                neg['wrong'] += 1
                neg['wrongkeys'].append(key)
        else:
            print "Label was not correctly assigned."

    print "Positive Samples Classified Correctly : " + str(pos['right'])
    print "Positive Samples Classified Incorrectly : " + str(pos['wrong'])
    print "Negative Samples Classified Correctly : " + str(neg['right'])
    print "Negative Samples Classified Incorrectly : " + str(neg['wrong'])


def feature_analysis():
    #features = r'([\+-]1)\s(\d:)(?P<f1>([\d\.]+))\s(\d:)(?P<f2>([\d\.]+))' +\
    #           r'\s(\d:)(?P<f3>([\d\.]+))'
    regv = r'[\+-]1\s.+\s2:([\d\.]+)'
    regs = r'[\+-]1\s.+\s4:([\d\.]+)'
    rego = r'[\+-]1\s.+\s6:([\d\.]+)'
    for key in data.keys():
        reg = re.match(regv, data[key]['features'])
        if reg is not None:
            verb.append(float(reg.group(1)))
        reg = re.match(regs, data[key]['features'])
        if reg is not None:
            subj.append(float(reg.group(1)))
        reg = re.match(rego, data[key]['features'])
        if reg is not None:
            obj.append(float(reg.group(1)))
    for vso in ['verb', 'subj', 'obj']:
        for vals in ['pr', 'pw', 'nr', 'nw']:
            featurelist[vso + vals] = []
    for key in pos['rightkeys']:
        #reg = re.match(features, data[key]['features'])
        reg = re.match(regv, data[key]['features'])
        if reg is not None:
            featurelist['verbpr'].append(reg.group(1))
        else:
            featurelist['verbpr'].append(-1)
        reg = re.match(regs, data[key]['features'])
        if reg is not None:
            featurelist['subjpr'].append(reg.group(1))
        else:
            featurelist['subjpr'].append(-1)
        reg = re.match(rego, data[key]['features'])
        if reg is not None:
            featurelist['objpr'].append(reg.group(1))
        else:
            featurelist['objpr'].append(-1)
    for key in neg['rightkeys']:
        reg = re.match(regv, data[key]['features'])
        if reg is not None:
            featurelist['verbnr'].append(reg.group(1))
        else:
            featurelist['verbnr'].append(-1)
        reg = re.match(regs, data[key]['features'])
        if reg is not None:
            featurelist['subjnr'].append(reg.group(1))
        else:
            featurelist['subjnr'].append(-1)
        reg = re.match(rego, data[key]['features'])
        if reg is not None:
            featurelist['objnr'].append(reg.group(1))
        else:
            featurelist['objnr'].append(-1)
    for key in pos['wrongkeys']:
        reg = re.match(regv, data[key]['features'])
        if reg is not None:
            featurelist['verbpw'].append(reg.group(1))
        else:
            featurelist['verbpw'].append(-1)
        reg = re.match(regs, data[key]['features'])
        if reg is not None:
            featurelist['subjpw'].append(reg.group(1))
        else:
            featurelist['subjpw'].append(-1)
        reg = re.match(rego, data[key]['features'])
        if reg is not None:
            featurelist['objpw'].append(reg.group(1))
        else:
            featurelist['objpw'].append(-1)
    for key in neg['wrongkeys']:
        reg = re.match(regv, data[key]['features'])
        if reg is not None:
            featurelist['verbnw'].append(reg.group(1))
        else:
            featurelist['verbnw'].append(-1)
        reg = re.match(regs, data[key]['features'])
        if reg is not None:
            featurelist['subjnw'].append(reg.group(1))
        else:
            featurelist['subjnw'].append(-1)
        reg = re.match(rego, data[key]['features'])
        if reg is not None:
            featurelist['objnw'].append(reg.group(1))
        else:
            featurelist['objnw'].append(-1)
    #----------------------------------------------------------
    # Desired
    plt.figure(1)
    plt.plot(featurelist['subjpr'], featurelist['verbpr'], 'ro')
    plt.plot(featurelist['subjpw'], featurelist['verbpw'], 'r^')
    plt.plot(featurelist['subjnr'], featurelist['verbnr'], 'bo')
    plt.plot(featurelist['subjnw'], featurelist['verbnw'], 'b^')
    plt.xlabel('subject')
    plt.ylabel('verb')
    plt.figure(2)
    plt.plot(featurelist['subjpr'], featurelist['objpr'], 'ro')
    plt.plot(featurelist['subjpw'], featurelist['objpw'], 'r^')
    plt.plot(featurelist['subjnr'], featurelist['objnr'], 'bo')
    plt.plot(featurelist['subjnw'], featurelist['objnw'], 'b^')
    plt.xlabel('subject')
    plt.ylabel('object')
    plt.figure(3)
    plt.plot(featurelist['objpr'], featurelist['verbpr'], 'ro')
    plt.plot(featurelist['objpw'], featurelist['verbpw'], 'r^')
    plt.plot(featurelist['objnr'], featurelist['verbnr'], 'bo')
    plt.plot(featurelist['objnw'], featurelist['verbnw'], 'b^')
    plt.xlabel('object')
    plt.ylabel('verb')
    #----------------------------------------------------------
    #plt.plot(featurelist['subjnr'].append(featurelist['subjnw']),
    #         featurelist['verbnr'].append(featurelist['verbnw']),
    #         'bo')
    #ax = plt.subplot(311)
    #plt.plot(range(len(featurelist['verbpr'])), featurelist['verbpr'], 'r-',
    #         label='True Positive')
    #plt.plot(range(len(featurelist['verbpw'])), featurelist['verbpw'], 'r--',
    #         label='False Negatives')
    #plt.plot(range(len(featurelist['verbnr'])), featurelist['verbnr'], 'b-',
    #         label='False Positives')
    #plt.plot(range(len(featurelist['verbnw'])), featurelist['verbnw'], 'b--',
    #         label='True Negatives')
    #plt.xlabel('verb')
    #plt.subplot(312)
    #plt.plot(range(len(featurelist['subjpr'])), featurelist['subjpr'], 'r-',
    #         range(len(featurelist['subjpw'])), featurelist['subjpw'], 'r--',
    #         range(len(featurelist['subjnr'])), featurelist['subjnr'], 'b-',
    #         range(len(featurelist['subjnw'])), featurelist['subjnw'], 'b--',)
    #plt.xlabel('subject')
    #plt.subplot(313)
    #plt.plot(range(len(featurelist['objpr'])), featurelist['objpr'], 'r-',
    #         range(len(featurelist['objpw'])), featurelist['objpw'], 'r--',
    #         range(len(featurelist['objnr'])), featurelist['objnr'], 'b-',
    #         range(len(featurelist['objnw'])), featurelist['objnw'], 'b--',)
    #plt.xlabel('object')
    #ax.legend(loc='upper right')
    plt.show()


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
        print re.sub(r'\<br /\>', '\\n', sent['depparse'])
        inp = raw_input()
        if inp == 'q':
            break


if __name__ == '__main__':
    confusion_matrix()
    feature_analysis()
    #list_sentences(real=1, pred=-1)
