from __future__ import print_function
from nltk.tokenize import word_tokenize


class Sentence:
    """
    This will house all the features of a particular sentence.
    From just the sentence to the tokenized words and maybe if
    required later, then the pos tags as well.
    TODO: 1. Remove stop words from self.words
    """

    def __init__(self, sentnc):
        self.sentence = sentnc
        self.words = word_tokenize(sentnc)

    def __str__(self):
        return unicode(self.sentence).encode('utf-8')

    def __getitem__(self, index):
        return self.words[index]
