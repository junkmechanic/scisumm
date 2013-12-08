from Document import Document
from Document import logit
from datetime import datetime
from Ranker import SectionMMR

logit('\n' + str(datetime.now()))

# number of sentences in the summary
num = 2
# maximum allowed length of the summary
MAXLEN = 200


def summarize_secitons(document, sections, coef=0.8):
    logit(document)
    for section_name in sections:
        doc = Document(document)
        all_sentences, all_offset = doc.all_sentences()
        sec_sentences, sec_offset = doc.section_sentences(section_name)
        limit = len(sec_sentences)

        # Ranker
        ranker = SectionMMR(all_sentences)
        ranker.rank(sec_offset=sec_offset, limit=limit, coef=coef)
        sentencs = ranker.scores

        summary = []
        for x in range(num):
            idx = sentencs[x][0] + sec_offset
            sent = doc[idx].sentence
            summary.append((sent, sentencs[x][1], doc.get_section_name(idx)))
        text = ''
        logit("\nSection : " + section_name)
        for sent, score, section in summary:
            #text += '\n' + "[" + section.encode('utf-8') + "] " + \
            #        "[" + str(score) + "] " + sent.encode('utf-8')
            text += '\n' + sent.encode('utf-8')
        logit(text)


if __name__ == '__main__':
    doc = '../demo/P07-3014-parscit-section.xml'
    sections = ['introduction', 'related work', 'method', 'evaluation']
    summarize_secitons(doc, sections, coef=0.7)