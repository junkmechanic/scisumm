from Document import Document
from Document import logit
from datetime import datetime
from Ranker import TextRank
import PythonROUGE

logit('\n' + str(datetime.now()))

# number of sentences in the summary
num = 9
# maximum allowed length of the summary
MAXLEN = 600


def summarize(document):
    doc = Document(document)
    sentences, offset = doc.all_sentences()

    # Ranker
    ranker = TextRank(sentences)
    scores = ranker.scores

    # Selector
    summary = []
    sum_len = 0
    for x in range(num):
        idx = scores[x][0] + offset
        sent = doc[idx].sentence
        if sum_len + len(sent.split(' ')) > MAXLEN:
            break
        summary.append((sent, scores[x][1], doc.get_section_name(idx)))
        sum_len += len(sent.split(' '))
    text = ''
    logit("\nP07-3014")
    logit("\nAll Sentences")
    #logit("\nFiltered Sentences")
    logit("Length of summary : " + str(sum_len))
    for sent, score, section in summary:
        text += '\n' + "[" + section.encode('utf-8') + "] " + \
                "[" + str(score) + "] " + sent.encode('utf-8')
    logit(text)

    # Printer
    # this has to be automated
    file = PythonROUGE.BASE_DIR + "data/Summary.txt"
    with open(file, 'w') as sfile:
        sfile.write('\n'.join([sent for sent, sc, sec in summary]).
                    encode('utf-8'))

    # Evaluator
    guess_summary_list = [file]
    ref_summary_list = [[PythonROUGE.BASE_DIR + "data/P07-3014-Ref.txt"]]
    recall, precision, F_measure = PythonROUGE.PythonROUGE(guess_summary_list,
                                                           ref_summary_list,
                                                           ngram_order=1)
    print recall, precision, F_measure

if __name__ == '__main__':
    doc = '../demo/P07-3014-parscit-section.xml'
    summarize(doc)
