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
#from operator import itemgetter


# this is a temporary list for debugging.
trees = []
test_data = OrderedDict()


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


def get_pos_sentences(infile, outfile, backup=False):
    doc = Document(infile)
    #sentences, o = doc.all_sentences()
    #ranker = Ranker(sentences, tfidf=False)
    #-----------------------------------------
    # Instead of the above, now sentences will be clubbed into sections and
    # passed to the ranker, which is to be returned
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    ranker = Ranker(sections)
    #-----------------------------------------
    sent, offset = doc.section_sentences('abstract')
    sent_idx = range(offset, offset + len(sent))
    samples = '\n'.join(sent)
    writeToFile(outfile, samples, 'w')
    #return ranker, sent_idx
    # The sent_idx needs to be converted to reflect the corresponding section
    # index
    section_idx = sent2Section(doc, sent_idx)
    if backup:
        backupfile = DIR['BASE'] + "data/backup.txt"
        writeToFile(backupfile, "\n---------Positive---------\n", 'a')
        writeToFile(backupfile, samples, 'a')
    return ranker, section_idx


def get_neg_sentences(infile, outfile, backup=False):
    doc = Document(infile)
    sentences, offset = doc.all_sentences()
    ranker = TextRank(sentences)
    ranker.rank()
    num = 5
    x = -1
    samples = ''
    sent_idx = []
    while num > 0:
        idx = ranker.scores[x][0] + offset
        x -= 1
        if not validSentence(doc[idx]):
            continue
        else:
            sent_idx.append(idx)
            samples += doc[idx].sentence.encode('utf-8') + '\n'
            num -= 1
    writeToFile(outfile, samples, 'w')
    #ranker = Ranker(sentences, tfidf=False)
    #return ranker, sent_idx
    #-----------------------------------------
    # Calculating the sectional TF-IDF
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    ranker = Ranker(sections)
    #-----------------------------------------
    # The sent_idx needs to be converted to reflect the corresponding section
    # index
    section_idx = sent2Section(doc, sent_idx)
    if backup:
        backupfile = DIR['BASE'] + "data/backup.txt"
        writeToFile(backupfile, "\n---------Negative---------\n", 'a')
        writeToFile(backupfile, samples, 'a')
    return ranker, section_idx


def get_test_sentences(infile, outfile, backup=False):
    doc = Document(infile)
    sentences, offset = doc.all_sentences()
    ranker = TextRank(sentences)
    ranker.rank()
    num = 7
    x = 0
    samples = ''
    sent_idx = []
    while num > 0:
        idx = ranker.scores[x][0] + offset
        x += 1
        #if not validSentence(doc[idx]):
        #    continue
        #else:
        #    sent_idx.append(idx)
        #    samples += doc[idx].sentence.encode('utf-8') + '\n'
        #    num -= 1
        sent_idx.append(idx)
        samples += doc[idx].sentence.encode('utf-8') + '\n'
        num -= 1
        #---------------------------------------------------
        # Storing the sentence in the dictionary for pickling for display
        key = infile + "-" + str(idx)
        test_data[key] = {'sentence': doc[idx].sentence.encode('utf-8'),
                          'textrank': ranker.scores[x - 1][1]}
    writeToFile(outfile, samples, 'w')
    #ranker = Ranker(sentences, tfidf=False)
    #return ranker, sent_idx
    #-----------------------------------------
    # Calculating the sectional TF-IDF
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    ranker = Ranker(sections)
    #-----------------------------------------
    # The sent_idx needs to be converted to reflect the corresponding section
    # index
    section_idx = sent2Section(doc, sent_idx)
    if backup:
        backupfile = DIR['BASE'] + "data/backup.txt"
        writeToFile(backupfile, "\n---------" + str(doc) + "---------\n", 'a')
        writeToFile(backupfile, samples, 'a')
    return ranker, section_idx


def validSentence(sentence):
    if len(sentence.words) < 15:
        return False
    if len(sentence.words) > 40:
        return False
    if re.search(r'[()\[\]]', str(sentence)) is not None:
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


def parseTrees(infile, outfile, ranker, sent_idx, label, sourcefile=None):
    current = dict()
    i = 0
    with open(infile, 'r') as file:
        for line in file.readlines():
            if len(line.strip()) == 0:
                processTree(outfile, current[0], ranker, sent_idx[i], label,
                            sourcefile)
                i += 1
                current = dict()
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


def processTree(outfile, root, ranker, idx, label, sourcefile=None):
    trees.append(root)
    verb_val = ranker.tfidf_value(idx, root.word)
    #-------------------------------------
    # For display
    root.value += '         ' + str(verb_val)
    #-------------------------------------
    #verb_val = ranker.total_count(root.word)
    # Look for subject
    subj = findNode(root, 'subj')
    subj_val = getValue(subj, ranker, idx)
    #-------------------------------------
    # For display
    if subj is not None:
        subj.value += '         ' + str(subj_val)
    #-------------------------------------
    obj = findNode(root, 'obj')
    obj_val = getValue(obj, ranker, idx)
    #-------------------------------------
    # For display
    if obj is not None:
        obj.value += '         ' + str(obj_val)
    #-------------------------------------
    # Adding the tree for pickling
    if sourcefile is not None:
        key = sourcefile + "-" + idx
        test_data[key]['dep-parse'] = root
    #-------------------------------------
    writeToFile(outfile, label + " 1:" + str(verb_val) + " 2:" +
                str(subj_val) + " 3:" + str(obj_val) + '\n', 'a')
    #-----------------------------------------------------------
    # Extra files with different combinations of features
    #datadir = DIR['BASE'] + "data/"
    #os.chdir(datadir)
    #writeToFile('f-verb-noun.txt', label + " 1:" + str(verb_val) +
    #            " 2:" + str((obj_val + subj_val) / 2) + '\n', 'a')
    #writeToFile('f-verb-subj.txt', label + " 1:" + str(verb_val) +
    #            " 2:" + str(subj_val) + '\n', 'a')
    #writeToFile('f-verb-obj.txt', label + " 1:" + str(verb_val) +
    #            " 3:" + str(obj_val) + '\n', 'a')
    #writeToFile('f-subj-obj.txt', label + " 1:" + str(subj_val) +
    #            " 2:" + str(obj_val) + '\n', 'a')
    #-----------------------------------------------------------


def getValue(node, ranker, idx):
    if node is None:
        return 0.0
        #return 0
    else:
        value, num = computeValue(node, ranker, idx)
        if value == 0.0:
            return 0.0
        else:
            return value / num
        #value, num = computeValue(node, ranker, idx)
        #if value == 0:
        #    return 0
        #else:
        #    return value


def computeValue(node, ranker, idx):
    if node.word.lower() in stopwords.words('english'):
        num = 0
        val = 0.0
        #val = 0
    else:
        # One case has still not been covered where the word might not be a
        # stopword but is still not included in the vectorized vocabulary.
        # The same is true for numbers.
        num = 1
        val = ranker.tfidf_value(idx, node.word)
        #-------------------------------------
        # For display
        node.value += str(val)
        #-------------------------------------
        #val = ranker.total_count(node.word)
    for child in node.children:
        value, n = computeValue(child, ranker, idx)
        val += value
        num += n
    return val, num


# Can experiment a few things such as:
#    leaving out stopwords [This has been taken care of in computeValue]
#    considering multiple occurances of subjects and objects
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


def generateFeatures():
    xmldir = DIR['BASE'] + "demo/"
    datadir = DIR['BASE'] + "data/"
    #infile = xmldir + 'P99-1026-parscit-section.xml'
    sentfile = datadir + 'sentences.txt'
    depfile = datadir + 'dependency-trees.txt'
    featurefile = datadir + 'features.txt'
    for infile in glob(xmldir + "*.xml"):
        try:
            print infile + " is being processed."
            # The following is for collecting summary sentences
            ranker, sent_idx = get_pos_sentences(infile, sentfile, backup=True)
            create_dep_parse(sentfile, depfile)
            parseTrees(depfile, featurefile, ranker, sent_idx, '+1')

            # The following is for negative samples
            ranker, sent_idx = get_neg_sentences(infile, sentfile, backup=True)
            create_dep_parse(sentfile, depfile)
            parseTrees(depfile, featurefile, ranker, sent_idx, '-1')

            # The following is for test samples
            ranker, sent_idx = get_test_sentences(infile, sentfile)
            create_dep_parse(sentfile, depfile)
            parseTrees(depfile, featurefile, ranker, sent_idx, '+1')
        except Exception as e:
            print(infile + str(e))
    print "All input files processed to create feature vectors."


#if __name__ == '__main__':
    #generateFeatures()
