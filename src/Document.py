from __future__ import print_function
import re
from lxml import etree
#from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from Sentence import Sentence
from collections import OrderedDict


def logit(text):
    print(text)
    try:
        with open('logfile.txt', "a") as outfile:
            outfile.write(text)
            outfile.write('\n')
    except Exception as e:
        print(str(e))


class Document:
    """
    The main object for Document processing.
    The following instance methods are avilable for use:
        1. all_text() : returns the entire block of text as a string
        2. all_sentences() : returns a list of all the sentences and the
           offset value which is 0 in this case.
        3. filtered_sentences() : returns a list of all the sentences filtered
           plus 0 as the offset value
        4. indexing an object of this class will return a Sentence object
           corresponding to that index
        5. get_section_name(sent_index) : takes a sentence index as input and
           returns the corresponding section that the sentence belongs to.
        6. section_sentences(section) : returns a list of all the sentences in
           a particular section and the offset value for that section.

    TODO: 1. Save the object as a pickle for later use
             and make provisions for importing such pickles
          2. Functions to print and return the document in different formats
          3. Check if the input file is actually present or not
    """

    def __init__(self, xmlfile):
        self.document = OrderedDict()
        self.process_doc(xmlfile)
        self.convert_to_obj()

    def __getitem__(self, index):
        for sec, blk in self.document.items():
            if index in blk.keys():
                return blk[index]
        # Raise Exception ideally
        print("The requested index is out of range of this doc !!")
        return Sentence('')

    def process_doc(self, xmlfile):

        # Set up sentence tokenizer
        punkt_param = PunktParameters()
        # Domain specific abbreviations
        punkt_param.abbrev_types = set(['e.g', 'al', 'i.e'])
        sent_tokenize = PunktSentenceTokenizer(punkt_param).tokenize

        tree = etree.parse(xmlfile)
        algrthms = tree.getroot()
        block = algrthms.iterdescendants(['sectionHeader', 'bodyText'])
        section = ''
        counter = 0
        sentences = []
        try:
            while True:
                blk = block.next()
                if(blk.tag == 'sectionHeader'):
                    section = blk.get('genericHeader')
                    # check if the next blk is bodytext. it might be a section
                    sentences = sent_tokenize(remove_crlf(block.next().text))
                    self.update_section(section,
                                        OrderedDict(enumerate(sentences,
                                                              start=counter)))
                else:
                    sentences = sent_tokenize(remove_crlf(blk.text))
                    self.update_section(section,
                                        OrderedDict(enumerate(sentences,
                                                              start=counter)))
                counter += len(sentences)
        except StopIteration:
            pass
        except Exception as e:
            logit("Something went wrong!")
            logit(section)
            logit(str(e))

    def update_section(self, section, sent_dict):
        if section in self.document.keys():
            self.document[section].update(sent_dict)
        else:
            self.document[section] = sent_dict

    def all_text(self):
        alltext = ''
        for sec, block in self.document.items():
            alltext += '\n' + sec + '\n'
            for key in sorted(block.keys()):
                alltext += str(block[key]) + '\n'
        return alltext

    def all_sentences(self):
        sentences = []
        for sec, block in self.document.items():
            for key in sorted(block.keys()):
                sentences.append(str(block[key]))
        return sentences, 0

    def filtered_sentences(self):
        sentences = []
        for sec, block in self.document.items():
            for key in sorted(block.keys()):
                sentences.append(' '.join(block[key].tokens).encode('utf-8'))
        return sentences, 0

    def convert_to_obj(self):
        for sec, block in self.document.items():
            for key in block.keys():
                block[key] = Sentence(block[key])

    def get_section_name(self, sent_index):
        for sec, blk in self.document.items():
            if sent_index in blk.keys():
                return sec
        raise Exception("Sentence Index out of range.")

    def section_sentences(self, section):
        sentences = []
        if section in self.document.keys():
            for index, sent in self.document[section].items():
                sentences.append(str(sent))
            return sentences, sorted(self.document[section].keys())[0]
        else:
            raise Exception("Section not found!")


def remove_crlf(text):
    text = re.sub(r'-\n', r'', text)
    text = re.sub(r'([^-])\n', r'\1 ', text)
    text = re.sub(r'^\n', r'', text)
    return text


if __name__ == '__main__':
    doc = Document('../demo/P99-1026-parscit-section.xml')
    #logit('\n'.join(doc.all_sentences()[0]))
    #logit(doc.all_sentences())
