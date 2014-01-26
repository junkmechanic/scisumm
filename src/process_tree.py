import re
import os
import subprocess
from collections import deque
from Document import Document
from Config import DIR
from Ranker import Ranker
from GetTrainingSamples import writeToFile
from nltk.corpus import stopwords


# this is a temporary list for debugging.
trees = []


class Node:
    def __init__(self, str):
        reg = re.match(r'(\d+)-\>([A-Za-z0-9]+)-([A-Z\$]+)\s\(([a-z_]+)\)',
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

    def append(self, node):
        self.children.append(node)

    def __str__(self):
        return (' ' * self.level * 2 + str(self.level) + '->' +
                self.word + '-' + self.pos + '-' + self.dep)


def get_sentences(infile, outfile):
    doc = Document(infile)
    sentences, o = doc.all_sentences()
    ranker = Ranker(sentences)
    sent, offset = doc.section_sentences('abstract')
    sent_idx = range(offset, offset + len(sent))
    samples = '\n'.join(sent)
    writeToFile(outfile, samples, 'w')
    print "Sentences written"
    return ranker, sent_idx


def create_dep_parse(infile, outfile):
    parserdir = DIR['BASE'] + "lib/Stanford-Parser/"
    os.chdir(parserdir)
    classpath = '.:./*'
    parser = 'ParsedTree'
    options = '--display'
    subprocess.call(['java', '-cp', classpath, parser, options, infile,
                     outfile])


def parseTrees(infile, ranker, sent_idx):
    current = dict()
    i = 0
    with open(infile, 'r') as file:
        for line in file.readlines():
            if len(line.strip()) == 0:
                processTree(current[0], ranker, sent_idx[i])
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


def processTree(root, ranker, idx):
    trees.append(root)
    verb_val = ranker.tfidf_value(idx, root.word)
    # Look for subject
    subj = findNode(root, 'subj')
    subj_val = getValue(subj, ranker, idx)
    print verb_val
    print subj_val
    printTree(root, ranker, idx)


def getValue(node, ranker, idx):
    if node is None:
        return 0.0
    else:
        value, num = computeValue(node, ranker, idx)
        return value / num


def computeValue(node, ranker, idx):
    if node.word in stopwords.words('english'):
        num = 0
        val = 0.0
    else:
        num = 1
        val = ranker.tfidf_value(idx, node.word)
    for child in node.children:
        value, n = computeValue(child, ranker, idx)
        val += value
        num += n
    return val, num


# Can experiment a few things such as:
#    leaving out stopwords
#    considering multiple subjects
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
        print str(child) + ' ' + str(ranker.tfidf_value(idx, child.word))
        printChildTree(child, ranker, idx)


if __name__ == '__main__':
    xmldir = DIR['BASE'] + "demo/"
    datadir = DIR['BASE'] + "data/"
    infile = xmldir + 'P99-1026-parscit-section.xml'
    sentfile = datadir + 'sentences.txt'
    depfile = datadir + 'dependency-trees.txt'
    ranker, sent_idx = get_sentences(infile, sentfile)
    create_dep_parse(sentfile, depfile)
    parseTrees(depfile, ranker, sent_idx)
