# coding=utf-8
from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import vstack
import networkx as nx
from operator import itemgetter


class Ranker:
    """
    This class is the superclass for all rankers and will contain common
    preprocessing steps required for all the rankers.
    But define your own Ranker subclass with the method rank() and any
    over-rides if necessary.

    The parameter passed to the constructor is a list containing all the
    sentences that need to be ranked. The Ranker can also be used to rank
    entire documents, if need be. In that case, each item in the list would
    represent a document and hence should contain a concatenated string of
    all the sentences in that document.

    This class provides the following attributes:
        - self.sentences
        - self.dtm :
            This is a matrix containing the count of each unigram in the
            given list of sentences. Hence, its dimensions are the m x n,
            where m is the length of the list passed (total number of
            sentences) and n is the number of unigrams present in the entire
            collection of sentences passed.
        - self.sim_matrix :
            This is a matrix representation of the undirected graph with the
            sentences as the vertices and the edges being defined by the
            co-occurance of unigrams in the corresponding pair of sentences.
        - self.scores :
            a list of tuples with sentence index and ranking metric
        - self.vectorizer
        - self.feature_names
    The instance methods provided by this base class:
        - tfidf_value()
    """

    def __init__(self, sentences):
        self.sentences = sentences
        self.vectorizer = TfidfVectorizer(min_df=1)
        self.dtm = self.vectorizer.fit_transform(sentences)
        self.sim_matrix = self.dtm * self.dtm.T
        self.feature_names = self.vectorizer.get_feature_names()

    def rank(self, **kwargs):
        not_defined = "The rank() method needs to be defined in the class " + \
                      "that inherits from Ranker class"
        raise NotImplementedError(not_defined)

    def tfidf_value(self, sent_idx, word):
        if word.lower() in self.feature_names:
            word_idx = self.feature_names.index(word.lower())
            return self.dtm.toarray()[sent_idx, word_idx]
        elif len(word.lower().split('-')) > 1:
            val = 0.0
            for part in word.lower().split('-'):
                val += self.tfidf_value(sent_idx, part)
            return val / len(word.lower().split('-'))
        else:
            print "No such word in the vocabulary: " + word
            return 0.0


class TextRank(Ranker):
    """
    This class is a wrapper around the implementation of TextRank algorithm
    from the networkx library

    The rank method should be implemented which should finally update the
    instance variable self.scores. This variable should be a ranked list
    of tuples with the first element in the tuple being the index of the
    sentence corresponding to the same in self.sentences and the second
    being the value based on which the sentences need to be ranked.
    """

    def rank(self, **kwargs):
        graph = nx.from_scipy_sparse_matrix(self.sim_matrix)
        scores = nx.pagerank(graph)
        self.scores = sorted(scores.items(), key=itemgetter(1), reverse=True)


class SectionMMR(Ranker):
    """
    This class is used to rank sentences in a particular seciton based on
    their importance within the section as well as their uniqueness
    compared to the sentences in the rest of the document. This is done using
    the following form of Maximal Marginal Relevance:
        MMR = λ * Sim1 (s) - (1 - λ) * Sim2 (s)
    where Sim1 is the similarity of the sentence w.r.t. the seciton and
    Sim2 is the similarity of the sentence w.r.t. the entire document and
    hence the MMR represents a convex combination of the two similarities.
    """

    def rank(self, sec_offset=None, limit=None, coef=0.7):
        """
        This instance method needs the starting index of the seciton in the
        document as well as the length (no. of sentences) in that section.
        """
        if limit is None:
            print("\nWARNING :You should provide the length of the section")
            limit = len(self.sentences)
        totlen = len(self.sentences)
        # Similarity of each sentence in the section with every other sentence
        # in that seciton
        sim1 = cosine_similarity(self.dtm[sec_offset:(sec_offset + limit)],
                                 self.dtm[sec_offset:(sec_offset + limit)])
        # For each sentence, get the mean of all its similarities
        sim1_sum = (sim1.sum(1) - 1) / (limit - 1)
        # rest will contain all the sentences except those in the current
        # section
        rest = vstack([self.dtm[0:sec_offset],
                       self.dtm[(sec_offset + limit):]])
        # Calculate the similarity of each section with each sentences in rest
        sim2 = cosine_similarity(self.dtm[sec_offset:(sec_offset + limit)],
                                 rest)
        sim2_sum = (sim2.sum(1) - 1) / (totlen - limit)
        mmr = (coef * sim1_sum) - ((1 - coef) * sim2_sum)
        self.scores = sorted(enumerate(mmr), key=itemgetter(1), reverse=True)
