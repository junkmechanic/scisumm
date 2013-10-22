from __future__ import print_function
import re
from datetime import datetime
from lxml import etree
from nltk.tokenize import sent_tokenize


def logit(text):
    print(text)
    with open('logfile1.txt', "a") as outfile:
        outfile.write(str(text))
        outfile.write('\n')


logit(str(datetime.now()))


class Document:
    """
    TODO: 1. Save the object as a pickle for later use
          and make provisions for importing such pickles
          2. Functions to print and return the document in different formats
    """

    def __init__(self, xmlfile):
        self.document = {}
        tree = etree.parse(xmlfile)
        algrthms = tree.getroot()
        block = algrthms.iterdescendants(['sectionHeader', 'bodyText'])
        section = ''
        counter = 0
        sentences = []
        try:
            #import pdb
            #pdb.set_trace()
            while True:
                blk = block.next()
                if(blk.tag == 'sectionHeader'):
                    section = blk.get('genericHeader')
                    sentences = sent_tokenize(remove_crlf(block.next().text))
                    self.update_section(section, dict(enumerate(sentences,
                                                                start=counter)
                                                      ))
                else:
                    sentences = sent_tokenize(remove_crlf(blk.text))
                    self.update_section(section,
                                        dict(enumerate(sentences,
                                                       start=counter)))
                counter += len(sentences)
        except StopIteration:
            pass
        except Exception as e:
            logit("Something went wrong!")
            logit(section)
            logit(str(e))
        for key, val in self.document.iteritems():
            logit(key)
            logit(val)

    def update_section(self, section, sent_dict):
        if section in self.document.keys():
            self.document[section].update(sent_dict)
        else:
            self.document[section] = sent_dict


def remove_crlf(text):
    text = re.sub(r'-\n', r'', text)
    text = re.sub(r'([^-])\n', r'\1 ', text)
    return text


if __name__ == '__main__':
    Document('../demo/E06-1050.xml')
