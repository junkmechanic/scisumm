from process_tree import create_dep_parse
from process_tree import parseTrees
from process_tree import sent2Section
from Document import Document
from Config import DIR
from Ranker import Ranker
from Ranker import TextRank
from GetTrainingSamples import writeToFile
import subprocess
import os


def classifyDoc(document):
    datadir = DIR['BASE'] + "data/"
    sentfile = datadir + 'sentences.txt'
    depfile = datadir + 'dependency-trees.txt'
    featurefile = datadir + 'features.txt'
    classify = DIR['BASE'] + "lib/svm-light/svm_classify"
    model = DIR['DATA'] + "sec-tfidf-model.txt"
    outfile = DIR['DATA'] + "svm-out-sent.txt"
    #sumlength = 5
    doc = Document(document)
    #-----------------------------------------
    # Clubbing sentences in sections and passing to the ranker
    sections = []
    for sec, block in doc.document.items():
        sentences = ''
        for key in sorted(block.keys()):
            sentences += (str(block[key]))
        sections.append(sentences)
    sec_ranker = Ranker(sections)
    sents, offset = doc.all_sentences()
    ranker = TextRank(sents)
    ranker.rank()
    looper = 20
    num = 10
    x = 0
    summary = []
    sent_idx = [0]
    sum_len = 0
    while num > 0:
        idx = ranker.scores[x][0] + offset
        x += 1
        sent_idx[0] = idx
        writeToFile(sentfile, doc[idx].sentence.encode('utf-8'), 'w')
        if os.path.isfile(depfile):
            print "dep file exists. Deleting.."
            os.remove(depfile)
        create_dep_parse(sentfile, depfile)
        #-----------------------------------------
        # The sent_idx needs to be converted to reflect the corresponding
        # section index
        sec_idx = sent2Section(doc, sent_idx)
        #-----------------------------------------
        if os.path.isfile(featurefile):
            print "dep file exists. Deleting.."
            os.remove(featurefile)
        parseTrees(depfile, featurefile, sec_ranker, sec_idx, '+1')
        if os.path.isfile(outfile):
            print "out file exists. Deleting.."
            os.remove(outfile)
        subprocess.call([classify, featurefile, model, outfile])
        with open(outfile, 'r') as ofile:
            sent_val = float(ofile.read().strip())
        if sent_val > 0:
            summary.append(doc[idx].sentence.encode('utf-8'))
            num -= 1
            sum_len += len(doc[idx].sentence.encode('utf-8').split(' '))
        if sum_len > 130:
            break
        looper -= 1
        if looper == 0:
            print "Looper Done"
            break
    writeToFile(datadir + "svm_summary.txt", '\n'.join(summary), 'w')
    print '\n'.join(summary)


def runClassifier():
    xmldir = DIR['BASE'] + "demo/"
    classifyDoc(xmldir + "W11-2821-parscit-section.xml")


if __name__ == '__main__':
    runClassifier()
