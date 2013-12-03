from Document import Document
from Document import logit
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import vstack
from operator import itemgetter

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
        totlen = len(all_sentences)
        sec_sentences, sec_offset = doc.section_sentences(section_name)
        limit = len(sec_sentences)

        # Ranker
        vectorizer = TfidfVectorizer()
        dtm = vectorizer.fit_transform(all_sentences)
        sim1 = cosine_similarity(dtm[sec_offset:(sec_offset + limit)],
                                 dtm[sec_offset:(sec_offset + limit)])
        sim1_sum = (sim1.sum(1) - 1) / (limit - 1)

        rest = vstack([dtm[0:sec_offset], dtm[(sec_offset + limit):]])
        sim2 = cosine_similarity(dtm[sec_offset:(sec_offset + limit)], rest)
        sim2_sum = (sim2.sum(1) - 1) / (totlen - limit)

        mmr = (coef * sim1_sum) - ((1 - coef) * sim2_sum)

        senten = list(enumerate(mmr))
        sentencs = sorted(senten, key=itemgetter(1), reverse=True)

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
