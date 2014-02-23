import re
from Config import DIR

pos = {}
neg = {}


def analyze(featurefile, outfile, outstring=None):
    if outstring is None:
        outstring = ''
    # To match the line number in files
    linenum = 1
    with open(featurefile, 'r') as ffile:
        for line in ffile.readlines():
            regex = re.search(r'([\+-]1)\s(.*)', line.strip())
            if regex.group(1) == '+1':
                pos[linenum] = regex.group(2)
            elif regex.group(1) == '-1':
                neg[linenum] = regex.group(2)
            else:
                print "Error : The features dont match the intended format"
                print "Error : " + line.strip()
            linenum += 1
    pos['right'] = 0
    pos['wrong'] = 0
    neg['right'] = 0
    neg['wrong'] = 0
    linenum = 1
    with open(outfile, 'r') as ffile:
        for line in ffile.readlines():
            outval = float(line.strip())
            if linenum in pos.keys():
                if outval > 0:
                    pos[linenum] = (1, outval, pos[linenum])
                    pos['right'] += 1
                else:
                    pos[linenum] = (0, outval, pos[linenum])
                    pos['wrong'] += 1
            elif linenum in neg.keys():
                if outval < 0:
                    neg[linenum] = (1, outval, neg[linenum])
                    neg['right'] += 1
                else:
                    neg[linenum] = (0, outval, neg[linenum])
                    neg['wrong'] += 1
            else:
                print "Line numbers dont match"
            linenum += 1
    precision = float(pos['right']) / float(pos['right'] + neg['wrong'])
    recall = float(pos['right']) / float(pos['right'] + pos['wrong'])
    resfile = DIR['DATA'] + "sec-tfidf-result.txt"
    with open(resfile, 'a') as resultfile:
        resultfile.write(outstring + '\n')
        resultfile.write("Positive Samples Classified Correctly : " +
                         str(pos['right']) + '\n')
        resultfile.write("Positive Samples Classified Incorrectly : " +
                         str(pos['wrong']) + '\n')
        resultfile.write("Negative Samples Classified Correctly : " +
                         str(neg['right']) + '\n')
        resultfile.write("Negative Samples Classified Incorrectly : " +
                         str(neg['wrong']) + '\n')
        resultfile.write("Precision :  {0}\tRecall : {1}\n".format(precision,
                                                                   recall))


possent = {}
negsent = {}


def with_sentences():
    linenum = 1
    sentfile = DIR['DATA'] + 'test-sentences.txt'
    with open(sentfile, 'r') as file:
        for line in file.readlines():
            if linenum in pos.keys():
                result, val, features = pos[linenum]
                possent[linenum] = (result, val, features, line.strip())
            elif linenum in neg.keys():
                result, val, features = neg[linenum]
                negsent[linenum] = (result, val, features, line.strip())
            else:
                print "Line numbers dont match"
            linenum += 1


def print_sentences():
    print "Positive sentences correctly classified :"
    for line, vals in possent.items():
        if vals[0] == 1:
            print "[" + str(vals[1]) + "] " + vals[3]
    print "Positive sentences wrongly classified :"
    for line, vals in possent.items():
        if vals[0] == 0:
            print "[" + str(vals[1]) + "] " + vals[3]
    print "Negative sentences correctly classified :"
    for line, vals in negsent.items():
        if vals[0] == 1:
            print vals[3]
    print "Negitive sentences wrongly classified :"
    for line, vals in negsent.items():
        if vals[0] == 1:
            print vals[3]
#with_sentences()
#print_sentences()
if __name__ == '__main__':
    featurefile = DIR['DATA'] + "train-features.txt"
    outfile = DIR['DATA'] + "sec-tfidf-train-out.txt"
    analyze(featurefile, outfile)
