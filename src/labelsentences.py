import re
import os
from collections import OrderedDict
from Document import Document
from Config import DIR
from Ranker import TextRank
from glob import glob
import logging
from train_data import validSentence, getContext, deleteFiles
import pickle


test_data = OrderedDict()


def generateTestFeatures(infile):
    doc = Document(infile)
    #------------------------------------------------
    # For display and analysis
    dir, filename = os.path.split(infile)
    fcode = re.match(r'(.+)-parscit-section\.xml', filename).group(1)
    #------------------------------------------------
    all_sentences, all_offset = doc.all_sentences()
    ranker = TextRank(all_sentences)
    ranker.rank()
    num = 7
    x = 0
    test_sents = []
    sent_indices = []
    while num > 0:
        idx = ranker.scores[x][0] + all_offset
        x += 1
        if not validSentence(doc[idx]):
            continue
        else:
            sent_indices.append(idx)
            test_sents.append(doc[idx].sentence.encode('utf-8'))
            num -= 1
        #------------------------------------------------
        # For display and analysis
        key = fcode + '-' + str(idx)
        test_data[key] = {'sentence': doc[idx].sentence.encode('utf-8'),
                          'textrank': ranker.scores[x - 1][1],
                          'contextpre': getContext(doc, idx, -2),
                          'contextpos': getContext(doc, idx, 2)}
    #-----------------------------------------
    for sentence, sent_idx in zip(test_sents, sent_indices):
        key = fcode + '-' + str(sent_idx)
        print test_data[key]['contextpre']
        print test_data[key]['sentence']
        print test_data[key]['contextpos']
        feature_string = raw_input()
        feature_string += '1'
        test_data[key]['reallbl'] = feature_string


def mainline():
    xmldir = DIR['BASE'] + "demo/"
    for infile in glob(xmldir + "*.xml"):
        try:
            print infile + " is being processed."
            generateTestFeatures(infile)
        except Exception as e:
            print "Some Exception in the main pipeline"
            print (str(type(e)))
            print str(e)
            logging.exception("Something awfull !!")
    pickleIt()


def pickleIt():
    picklefile = DIR['DATA'] + 'test-labels-pickle'
    deleteFiles([picklefile])
    with open(picklefile, 'wb') as pfile:
        pickle.dump(test_data, pfile)


if __name__ == '__main__':
    mainline()
