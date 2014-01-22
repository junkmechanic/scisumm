import re
import os
import subprocess
from Document import Document
from Config import DIR
#from Ranker import Ranker
from GetTrainingSamples import writeToFile


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
    sent, offset = doc.section_sentences('abstract')
    samples = '\n'.join(sent)
    writeToFile(outfile, samples, 'w')
    print "Sentences written"


def create_dep_parse(infile, outfile):
    parserdir = DIR['BASE'] + "lib/Stanford-Parser/"
    os.chdir(parserdir)
    classpath = '.:./*'
    parser = 'ParsedTree'
    options = '--display'
    subprocess.call(['java', '-cp', classpath, parser, options, infile,
                     outfile])


def parseTrees(infile):
    current = dict()
    with open(infile, 'r') as file:
        for line in file.readlines():
            if len(line.strip()) == 0:
                processTree(current[0])
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


def processTree(root):
    printTree(root)


def printTree(root):
    print root
    printChildTree(root)


def printChildTree(node):
    for child in node.children:
        print child
        printChildTree(child)


if __name__ == '__main__':
    xmldir = DIR['BASE'] + "demo/"
    datadir = DIR['BASE'] + "data/"
    infile = xmldir + 'P99-1026-parscit-section.xml'
    sentfile = datadir + 'sentences.txt'
    depfile = datadir + 'dependency-trees.txt'
    get_sentences(infile, sentfile)
    create_dep_parse(sentfile, depfile)
    parseTrees(depfile)
