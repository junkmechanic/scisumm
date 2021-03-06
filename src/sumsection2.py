from Document import Document
from Document import logit
from datetime import datetime
from Ranker import TextRank
from Config import DIR
from PythonROUGE import PythonROUGE

logit('\n' + str(datetime.now()))

# number of sentences in the summary
num = 1
# maximum allowed length of the summary
MAXLEN = 200


def summarize_secitons(document, sections):
    logit(document)
    doc = Document(document)
    all_sentences, all_offset = doc.all_sentences()
    summ = []
    for section_name in sections:
        sec_sentences, sec_offset = doc.section_sentences(section_name)

        # Ranker
        ranker = TextRank(sec_sentences)
        ranker.rank()
        sentencs = ranker.scores

        summary = []
        for x in range(num):
            idx = sentencs[x][0] + sec_offset
            sent = doc[idx].sentence
            summary.append((sent, sentencs[x][1], doc.get_section_name(idx)))
            summ.append(sent)
        text = ''
        logit("\nSection : " + section_name)
        for sent, score, section in summary:
            text += '\n' + sent.encode('utf-8')
        logit(text)
    file = DIR['BASE'] + "data/Summary.txt"
    with open(file, 'w') as sfile:
        sfile.write('\n'.join(summ).encode('utf-8'))

    # Evaluator
    guess_summary_list = [file]
    ref_summary_list = [[DIR['BASE'] + "data/P10-1024-Ref1.txt"]]
    recall, precision, F_measure = PythonROUGE(guess_summary_list,
                                               ref_summary_list,
                                               ngram_order=1)
    logit("Recall:{0} ; Precision:{1} ; F:{2}".format(recall, precision,
                                                      F_measure))


if __name__ == '__main__':
    doc = '../demo/P10-1024-parscit-section.xml'
    sections = ['introduction', 'method', 'conclusions']
    summarize_secitons(doc, sections)
