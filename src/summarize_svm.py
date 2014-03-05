from Document import Document
from Config import DIR
from Ranker import Ranker
from Ranker import TextRank
from GetTrainingSamples import writeToFile
from parseClient import getConnection, getDepParse
import subprocess
from train_data import deleteFiles, parseTrees, sent2Section, processTree
from train_data import validSentence


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
    looper = 20
    num = 10
    x = 0
    summary = []
    sent_idx = [0]
    sum_len = 0
    while num > 0:
        idx = ranker.scores[x][0] + offset
        x += 1
        if not validSentence(doc[idx]):
            continue
        elif doc.get_section_name(idx) == 'abstract':
            continue
        sent_idx[0] = idx
        #-----------------------------------------
        # dependency parse
        tree = parseTrees(getDepParse(client_socket,
                                      doc[idx].sentence.encode('utf-8')))
        #-----------------------------------------
        # The sent_idx needs to be converted to reflect the corresponding
        # section index
        sec_idx = sent2Section(doc, sent_idx)
        #-----------------------------------------
        deleteFiles([featurefile])
        feature_string = "+1"
        feature_string += processTree(tree, sec_ranker, sec_idx[0], False)
        writeToFile(featurefile, feature_string + '\n', 'a')
        deleteFiles([outfile])
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
    writeToFile(DIR['DATA'] + "svm_summary.txt", '\n'.join(summary), 'w')
    print '\n'.join(summary)


def runClassifier():
    xmldir = DIR['BASE'] + "demo/test/"
    classifyDoc(xmldir + "W11-2821-parscit-section.xml")


if __name__ == '__main__':
    runClassifier()
