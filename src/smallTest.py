import pickle
from Config import DIR
from random import choice
from analysis import analyze
from utilityFunctions import writeToFile, trainSvm, predictSvm, deleteFiles


picklefile = DIR['DATA'] + 'test-sentences-pickle'
with open(picklefile, 'rb') as pfile:
    global data
    data = pickle.load(pfile)

datadir = DIR['BASE'] + "data/"
model = DIR['DATA'] + "sec-tfidf-model-small.txt"
featurefile = datadir + 'features-small.txt'
outfile = DIR['DATA'] + "sec-tfidf-train-out-small.txt"
resfile = DIR['DATA'] + "sec-tfidf-result-small.txt"
deleteFiles([model, featurefile, outfile, resfile])

bucket = data.keys()

precision = []
recall = []

all_sets = []

#for i in range(07):
#    train_set = list(bucket)
#    test_set = []
#    for k in range(11):
#        curr = choice(train_set)
#        test_set.append(curr)
#        train_set.remove(curr)

for i in range(07):
    set = []
    for k in range(11):
        curr = choice(bucket)
        set.append(curr)
        bucket.remove(curr)
    all_sets.append(set)

for i in range(07):
    test_set = all_sets[i]
    train_set = []
    for set in [all_sets[z] for z in range(07) if z != i]:
        train_set.extend(set)
    for key in train_set:
        writeToFile(featurefile, data[key]['features'] + '\n', 'a')
    trainSvm(featurefile, model, gamma=1)
    predictSvm(featurefile, model, outfile)
    outstring = "Training Fold : " + str(i)
    print "************* " + outstring + " *************"
    analyze(featurefile, outfile, resfile, outstring)

    deleteFiles([featurefile, outfile])

    for key in test_set:
        writeToFile(featurefile, data[key]['features'] + '\n', 'a')
    predictSvm(featurefile, model, outfile)
    outstring = "Testing Fold : " + str(i)
    pre, rec = analyze(featurefile, outfile, resfile, outstring)
    precision.append(pre)
    recall.append(rec)

print precision
print sum(precision) / float(len(precision))
print recall
print sum(recall) / float(len(recall))
