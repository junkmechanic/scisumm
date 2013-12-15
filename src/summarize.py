from Document import Document
from Document import logit
from datetime import datetime
from Ranker import TextRank
from Config import DIR
#from PythonROUGE import PythonROUGE

logit('\n' + str(datetime.now()))

# number of sentences in the summary
num = 5
# maximum allowed length of the summary
MAXLEN = 130


def summarize(document, all=True):
    doc = Document(document)
    sentences, offset = (doc.all_sentences() if all
                         else doc.filtered_sentences())

    # Ranker
    ranker = TextRank(sentences)
    ranker.rank()
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
    logit("\nAll Sentences" if all else "\nFiltered Sentences")
    logit("Length of summary : " + str(sum_len))
    for sent, score, section in summary:
        text += '\n' + "[" + section.encode('utf-8') + "] " + \
                sent.encode('utf-8')
                #"[" + str(score) + "] " + sent.encode('utf-8')
    logit(text)

    # Printer
    # this has to be automated
    file = DIR['BASE'] + "data/Summary.txt"
    with open(file, 'w') as sfile:
        sfile.write('\n'.join([sent for sent, sc, sec in summary]).
                    encode('utf-8'))

    ## Evaluator
    #guess_summary_list = [file]
    #ref_summary_list = [[DIR['BASE'] + "data/C08-1122-Ref.txt"]]
    #recall, precision, F_measure = PythonROUGE(guess_summary_list,
    #                                           ref_summary_list,
    #                                           ngram_order=1)
    #logit("Recall:{0} ; Precision:{1} ; F:{2}".format(recall, precision,
    #                                                  F_measure))

if __name__ == '__main__':
    doc = '../demo/C08-1122-parscit-section.xml'
    summarize(doc, all=False)
