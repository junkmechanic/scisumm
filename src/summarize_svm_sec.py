from Document import Document
from Config import DIR
from Ranker import Ranker
from Ranker import TextRank
from GetTrainingSamples import writeToFile
from parseClient import getConnection, getDepParse
import subprocess
from train_data import deleteFiles, parseTrees, sent2Section, processTree
from train_data import getSecRankedSent
from operator import itemgetter


def classifyDoc(document):
    featurefile = DIR['DATA'] + 'features_svm.txt'
    classify = DIR['BASE'] + "lib/svm-light/svm_classify"
    model = DIR['DATA'] + "sec-tfidf-model.txt"
    outfile = DIR['DATA'] + "svm-out-sent.txt"
    #sumlength = 5
    client_socket = getConnection()
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
    #-----------------------------------------
    sents, sent_indices = getSecRankedSent(doc)
    #-----------------------------------------
    # The sent_idx needs to be converted to reflect the corresponding
    # section index
    sec_indices = sent2Section(doc, sent_indices)
    summary = []
    classified = []
    sum_len = 0
    for sent, sec_idx in zip(sents, sec_indices):
        #-----------------------------------------
        # dependency parse
        tree = parseTrees(getDepParse(client_socket, sent))
        #-----------------------------------------
        deleteFiles([featurefile])
        feature_string = "+1"
        feature_string += processTree(tree, sec_ranker, sec_idx, False)
        writeToFile(featurefile, feature_string + '\n', 'a')
        deleteFiles([outfile])
        subprocess.call([classify, featurefile, model, outfile])
        with open(outfile, 'r') as ofile:
            sent_val = float(ofile.read().strip())
            classified.append((sent, sent_val))
    for sent, val in sorted(classified, key=itemgetter(1)):
        summary.append(sent)
        sum_len += len(sent.split(' '))
        if sum_len > 130:
            break
    writeToFile(DIR['DATA'] + "svm_summary.txt", '\n'.join(summary), 'w')
    print '\n'.join(summary)


def runClassifier():
    xmldir = DIR['BASE'] + "demo/test/"
    classifyDoc(xmldir + "W11-2821-parscit-section.xml")


if __name__ == '__main__':
    runClassifier()
