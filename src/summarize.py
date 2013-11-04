from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.feature_extraction.text import CountVectorizer
from Document import Document
from operator import itemgetter
import networkx as nx
from Document import logit

doc = Document('../demo/P99-1026-parscit-section.xml')
sentences = doc.all_sentences()
vectorizer = TfidfVectorizer(min_df=2)
dtm = vectorizer.fit_transform(sentences)
sim_matrix = dtm * dtm.T
graph = nx.from_scipy_sparse_matrix(sim_matrix)
scores = nx.pagerank(graph)
scores = sorted(scores.items(), key=itemgetter(1), reverse=True)
summary = []
# number of sentences in the summary
num = 5
for x in range(num):
    summary.append((doc[scores[x][0]].sentence, scores[x][1]))
text = ''
for sent, score in summary:
    text += '\n' + sent
logit(text)
