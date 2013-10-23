from __future__ import print_function
import re
from datetime import datetime
from lxml import etree
from nltk.tokenize import sent_tokenize


def logit(text):
    print(text)
    with open('logfile1.txt', "a") as outfile:
        outfile.write(text.encode('utf8'))
        outfile.write('\n')


logit('\n' + str(datetime.now()))


class Document:
    """
    TODO: 1. Save the object as a pickle for later use
             and make provisions for importing such pickles
          2. Functions to print and return the document in different formats
          3. Check if the input file is actually present or not
    """

    def __init__(self, xmlfile):
        self.document = {}
        self.process_doc(xmlfile)

    def process_doc(self, xmlfile):
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
                alltext += block[key]  # + '\n'
        return alltext


def remove_crlf(text):
    text = re.sub(r'-\n', r'', text)
    text = re.sub(r'([^-])\n', r'\1 ', text)
    text = re.sub(r'^\n', r'', text)
    return text


if __name__ == '__main__':
    doc = Document('../demo/E06-1050.xml')
    logit(doc.all_text())
