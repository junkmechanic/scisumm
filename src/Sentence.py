from __future__ import print_function
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re


class Sentence:
    """
    This will house all the features of a particular sentence.
    From just the sentence to the tokenized words and maybe if
    required later, then the pos tags as well.

    Following are the attributes available currently:
        sentence : the entire sentence
        words : each word in the sentence (maybe this is not required)
        tokens : words after removing stopwords, puctiations etc.

    TODO: 1.
    """

    def __init__(self, sentnc):
        self.sentence = sentnc

        # Remember to encode the words in unicode when referecing the
        # following attribute
        self.words = word_tokenize(sentnc)
        self.tokens = self.filter_words()

    def filter_words(self):

        def strip_char(word):
            # Remove sorrounding qoutes
            word = re.sub(r'"(.*)"', r'\1', word)
            word = re.sub(r"'(.*)'", r'\1', word)
            return word

        # Unwanted charaters/words to be removed from the wordlist
        unwanted = [',', '.', '(', ')', ':', '"', "'", ';', "'s", '']
        remove_words = stopwords.words('english')
        remove_words.extend(unwanted)
        tokens = [w.lower() for w in self.words
                  if w.lower() not in remove_words]
        return(map(strip_char, tokens))

    def __str__(self):
        return unicode(self.sentence)

    def __getitem__(self, index):
        return self.tokens[index]
