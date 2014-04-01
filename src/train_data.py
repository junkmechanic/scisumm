import re
import os
import subprocess
from collections import deque
from collections import OrderedDict
from Document import Document
from Config import DIR
from Ranker import Ranker
from Ranker import TextRank
from GetTrainingSamples import writeToFile
from nltk.corpus import stopwords
from glob import glob
from parseClient import getConnection, getDepParse
import logging
import pickle
from analysis import analyze
#from operator import itemgetter


# this is a temporary list for debugging.
trees = []
# This will be used for pickling. The keys are:
#     svm-val
#     depparse
#     textrank
#     sentence
#     contextpre
#     contextpos
test_data = OrderedDict()
train_data = OrderedDict()
test_labels = {}
client_socket = None

newstopwords = stopwords.words('english')[:]
for word in ['we', 'us', 'our', 'ours', 'i', 'my', 'mine', 'they', 'them',
             'their', 'theirs']:
    if word in newstopwords:
        newstopwords.remove(word)


class Node:
    def __init__(self, str):
        reg = re.match(r'(\d+)-\>(.+)-([A-Z\$]+)\s\(([a-z_]+)\)',
                       str)
        if reg is None:
            print str
            print "Some fatal error. String not in expected format."
        else:
            self.level = int(reg.group(1))
            self.word = reg.group(2)
            self.pos = reg.group(3)
            self.dep = reg.group(4)
            self.children = []
            self.value = ''

    def append(self, node):
        self.children.append(node)

    def __str__(self):
        return (' ' * self.level * 2 + str(self.level) + '->' +
                self.word + '-' + self.pos + '-' + self.dep +
                '    ' + self.value)

    def html(self):
        return ('---' * self.level * 2 + '->' +
                self.word + '---' + self.pos + '---' + self.dep +
                '-----' + self.value)


def sent2Section(doc, sent_idx):
    section_idx = []
    for idx in sent_idx:
        section = 0
        for sec, blk in doc.document.items():
            if idx in blk.keys():
                break
            section += 1
        section_idx.append(section)
    return section_idx


def validSentence(sentence):
    if len(sentence.words) < 15:
        return False
    if len(sentence.words) > 40:
        return False
    if re.search(r'[()^+*#@/\\\[\]]', str(sentence)) is not None:
        return False
    return True


def create_dep_parse(infile, outfile):
    parserdir = DIR['BASE'] + "lib/Stanford-Parser/"
    os.chdir(parserdir)
    classpath = '.:./*'
    parser = 'ParsedTree'
    options = '--display'
    subprocess.call(['java', '-cp', classpath, parser, options, infile,
                     outfile])


def parseTrees(treestring):
    current = dict()
    for line in treestring.split('\n'):
        if len(line.strip()) == 0:
            return current[0]
        else:
            node = Node(line.strip())
            parent_level = node.level - 1
            if parent_level in current.keys():
                current[parent_level].append(node)
            elif node.level == 0:
                current[0] = node
            else:
                print "Fatal error: parent level does not exist."
            current[node.level] = node
    print "All dependency trees parsed successfully."


def processTree(root, ranker, idx, count=False):
    #trees.append(root)
    #if count:
    #    verb_val = ranker.total_count(root.word)
    #else:
    #    verb_val = ranker.tfidf_value(idx, root.word)
    if root.word.lower() in newstopwords:
        verb_val = 0.0
    else:
        verb_val = ranker.tfidf_value(idx, root.word)
    #verb_val = getValue(root, ranker, idx, count)
    #-------------------------------------
    # For display
    root.value += '         ' + str(verb_val)
    #-------------------------------------
    # Look for subject
    subj = findNode(root, 'subj')
    subj_val = getValue(subj, ranker, idx, count)
    #-------------------------------------
    # For display
    if subj is not None:
        subj.value += '         ' + str(subj_val)
    #-------------------------------------
    obj = findNode(root, 'obj')
    obj_val = getValue(obj, ranker, idx, count)
    #-------------------------------------
    # For display
    if obj is not None:
        obj.value += '         ' + str(obj_val)
    #-------------------------------------
    if count:
        return(" 4:" + str(verb_val) + " 5:" + str(subj_val) +
               " 6:" + str(obj_val))
    else:
        return(" 1:" + str(verb_val) + " 2:" + str(subj_val) +
               " 3:" + str(obj_val))


def getValue(node, ranker, idx, count):
    if node is None:
        return 0.0
    else:
        value, num = computeValue(node, ranker, idx, count)
        if value == 0.0:
            return 0.0
        else:
            if count:
                return value
            else:
                return value / num


def computeValue(node, ranker, idx, count=False):
    if node.word.lower() in newstopwords:
        num = 0
        val = 0.0
    else:
        # One case has still not been covered where the word might not be a
        # stopword but is still not included in the vectorized vocabulary.
        # The same is true for numbers.
        num = 1
        if count:
            val = ranker.total_count(node.word)
        else:
            val = ranker.tfidf_value(idx, node.word)
        #-------------------------------------
        # For display
        node.value += str(val)
        #-------------------------------------
    for child in node.children:
        value, n = computeValue(child, ranker, idx, count)
        val += value
        num += n
    return val, num


def findNode(node, pattern):
    pat = re.compile(pattern)
    if pat.search(node.dep) is not None:
        return node
    que = deque(node.children)
    while que:
        child = que.popleft()
        if pat.search(child.dep) is not None:
            return child
            #print 'Found ' + str(child)
            # To remove stopwords
            #if child.word == 'It':
            #    continue
            #else:
            #    break
        else:
            #print 'Not Found Yet' + str(child)
            que.extend(child.children)
    return None


# This is Depth First
def findNode_DFS(node, pattern):
    pat = re.compile(pattern)
    if pat.search(node.dep) is not None:
        return node
    for child in node.children:
        found = findNode(child, pattern)
        if found is not None:
            return found
    return None


def printTree(root, ranker=None, idx=None):
    print root
    printChildTree(root, ranker, idx)


def printChildTree(node, ranker=None, idx=None):
    for child in node.children:
        if ranker is not None:
            print str(child) + '    ' +\
                str(ranker.tfidf_value(idx, child.word))
        else:
            print str(child)
        printChildTree(child, ranker, idx)


def getTree(root):
    treestring = str(root) + '\n'
    treestring += getChildTree(root)
    return treestring


def getChildTree(node):
    tstring = ""
    for child in node.children:
        tstring += str(child) + '\n'
        tstring += getChildTree(child)
    return tstring


def getContext(doc, idx, reach):
    context = ''
    if reach > 0:
        lines = [idx + r for r in range(reach + 1)][1:]
    else:
        lines = [idx - r for r in reversed(range(-reach + 1))][:-1]
    for lidx in lines:
        #print "Sentence number " + str(lidx)
        #print(doc[lidx].sentence.encode('utf-8'))
        if doc[lidx] is not None:
            context += doc[lidx].sentence.encode('utf-8') + " "
        else:
            print "Index out of range of Document : " + str(lidx)
    return context


def generateTrainFeatures(client_socket, infile, featurefile):
    #------------------------------------------------
    doc = Document(infile)
    all_sentences, all_offset = doc.all_sentences()
    #------------------------------------------------
    # Positive sentences
    pos_sents, offset = doc.section_sentences('abstract')
    sent_indices = range(offset, offset + len(pos_sents))
    #-----------------------------------------
    # Sectional Ranker
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    sec_ranker = Ranker(sections)
    sec_indices = sent2Section(doc, sent_indices)
    #-----------------------------------------
    # Count ranker
    #count_ranker = Ranker(all_sentences, tfidf=False)
    #-----------------------------------------
    for sentence, sent_idx, sec_idx in zip(pos_sents, sent_indices,
                                           sec_indices):
        feature_string = '+1'
        tree = parseTrees(getDepParse(client_socket, sentence))
        feature_string += processTree(tree, sec_ranker, sec_idx, False)
        #feature_string += processTree(tree, count_ranker, sent_idx, True)
        writeToFile(featurefile, feature_string + '\n', 'a')
    #------------------------------------------------
    # Negative sentences
    neg_ranker = TextRank(all_sentences)
    neg_ranker.rank()
    num = 5
    x = -1
    neg_sents = []
    sent_indices = []
    while num > 0:
        idx = neg_ranker.scores[x][0] + all_offset
        x -= 1
        if not validSentence(doc[idx]):
            continue
        else:
            sent_indices.append(idx)
            neg_sents.append(doc[idx].sentence.encode('utf-8'))
            num -= 1
    sec_indices = sent2Section(doc, sent_indices)
    #------------------------------------------------
    for sentence, sent_idx, sec_idx in zip(neg_sents, sent_indices,
                                           sec_indices):
        feature_string = '-1'
        tree = parseTrees(getDepParse(client_socket, sentence))
        feature_string += processTree(tree, sec_ranker, sec_idx, False)
        #feature_string += processTree(tree, count_ranker, sent_idx, True)
        writeToFile(featurefile, feature_string + '\n', 'a')
    #------------------------------------------------
    print "All input files processed to create feature vectors for training."


def getSecRankedSent(doc):
    sections = ['introduction', 'method', 'conclusions']
    test_sents = []
    sent_indices = []
    for section_name in sections:
        sec_sentences, sec_offset = doc.section_sentences(section_name)
        ranker = TextRank(sec_sentences)
        ranker.rank()
        num = 5
        for x in range(len(ranker.scores)):
            idx = ranker.scores[x][0] + sec_offset
            if not validSentence(doc[idx]):
                continue
            sent_indices.append(idx)
            test_sents.append(doc[idx].sentence.encode('utf-8'))
            num -= 1
            if num == 0:
                break
        print len(test_sents)
        #------------------------------------------------
    return test_sents, sent_indices


def getRankedSent(doc, fcode):
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
        sent_indices.append(idx)
        test_sents.append(doc[idx].sentence.encode('utf-8'))
        num -= 1
        #------------------------------------------------
        # For display and analysis
        key = fcode + '-' + str(idx)
        test_data[key] = {'sentence': doc[idx].sentence.encode('utf-8'),
                          'textrank': ranker.scores[x - 1][1],
                          'contextpre': getContext(doc, idx, -2),
                          'contextpos': getContext(doc, idx, 2),
                          'reallbl': getLabel(key)}
        #if getLabel(key) == 0:
        #    # Ask for value
        #    pass
        #else:
        #    test_data[key]['reallbl'] = getLabel(key)
        #------------------------------------------------
    return test_sents, sent_indices


def getLabel(key):
    global test_labels
    if key in test_labels.keys():
        if 'reallbl' in test_labels[key].keys():
            return test_labels[key]['reallbl']
        else:
            print "Label not found for " + key
            return 0
    else:
        print "Key not found. Sentence has not been labelled."


def generateTestFeatures(client_socket, infile, featurefile):
    #------------------------------------------------
    doc = Document(infile)
    #------------------------------------------------
    # Load pickle for label
    picklefile = DIR['DATA'] + 'test-labels-pickle'
    global test_labels
    with open(picklefile, 'rb') as pfile:
        test_labels = pickle.load(pfile)
    #------------------------------------------------
    # For display and analysis
    dir, filename = os.path.split(infile)
    fcode = re.match(r'(.+)-parscit-section\.xml', filename).group(1)
    #------------------------------------------------
    test_sents, sent_indices = getRankedSent(doc, fcode)
    #-----------------------------------------
    # Sectional Ranker
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    sec_ranker = Ranker(sections)
    sec_indices = sent2Section(doc, sent_indices)
    #-----------------------------------------
    for sentence, sent_idx, sec_idx in zip(test_sents, sent_indices,
                                           sec_indices):
        key = fcode + '-' + str(sent_idx)
        feature_string = test_data[key]['reallbl']
        tree = parseTrees(getDepParse(client_socket, sentence))
        feature_string += processTree(tree, sec_ranker, sec_idx, False)
        test_data[key]['depparse'] = getTree(tree)
        test_data[key]['features'] = feature_string
        writeToFile(featurefile, feature_string + '\n', 'a')
    #------------------------------------------------


def mainline(train=False):
    datadir = DIR['BASE'] + "data/"
    if train is True:
        featurefile = datadir + 'train-features.txt'
        xmldir = DIR['BASE'] + "demo/train/"
    else:
        featurefile = datadir + 'test-features.txt'
        xmldir = DIR['BASE'] + "demo/test/"
    deleteFiles([featurefile])
    #infile = xmldir + 'C08-1122-parscit-section.xml'
    client_socket = getConnection()
    for infile in glob(xmldir + "*.xml"):
        try:
            print infile + " is being processed."
            if train is True:
                generateTrainFeatures(client_socket, infile, featurefile)
            else:
                generateTestFeatures(client_socket, infile, featurefile)
        except Exception as e:
            print "Some Exception in the main pipeline"
            print (str(type(e)))
            print str(e)
            logging.exception("Something awfull !!")
    model = DIR['DATA'] + "sec-tfidf-model.txt"
    if train is False:
        # TESTING
        outfile = DIR['DATA'] + "sec-tfidf-test-out.txt"
        predictSvm(featurefile, model, outfile)
        outstring = "Default values Test results"
        analyze(featurefile, outfile, outstring=outstring)
        pickleIt()
    else:
        # TRAINING
        trainSvm(featurefile, model)
        outfile = DIR['DATA'] + "sec-tfidf-train-out.txt"
        predictSvm(featurefile, model, outfile)
        outstring = "Default values"
        analyze(featurefile, outfile, outstring=outstring)


def trainSvm(featurefile, modelfile, gamma=1):
    learn = DIR['BASE'] + "lib/svm-light/svm_learn"
    #model = DIR['DATA'] + "sec-tfidf-model.txt"
    subprocess.call([learn, '-t', '2', '-x', '1', '-g', str(gamma),
                     featurefile, modelfile])


def pickleIt():
    picklefile = DIR['DATA'] + 'test-sentences-pickle'
    deleteFiles([picklefile])
    with open(picklefile, 'wb') as pfile:
        pickle.dump(test_data, pfile)


def predictSvm(featurefile, model, outfile):
    classify = DIR['BASE'] + "lib/svm-light/svm_classify"
    #model = DIR['DATA'] + "sec-tfidf-model.txt"
    subprocess.call([classify, featurefile, model, outfile])
    outlist = []
    with open(outfile, 'r') as ofile:
        for line in ofile.readlines():
            outlist.append(float(line.strip()))
    for key, val in zip(test_data.keys(), outlist):
        test_data[key]['svmval'] = val


def deleteFiles(flist):
    for file in flist:
        if os.path.isfile(file):
            d, f = os.path.split(file)
            print f + " exists. Deleting.."
            os.remove(file)


if __name__ == '__main__':
    mainline(False)
