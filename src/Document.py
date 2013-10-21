from lxml import etree
from nltk.tokenize import sent_tokenize


class Document:

    def __init__(self, xmlfile):
        self.document = {}
        tree = etree.parse(xmlfile)
        algrthms = tree.getroot()
        block = algrthms.iterdescendants(['sectionHeader', 'bodyText'])
        try:
            section = ''
            while True:
                blk = block.next()
                if(blk.tag == 'sectionHeader'):
                    self.document[blk.text] = sent_tokenize(
                        block.next().text)
                    section = blk.text
                else:
                    self.document[section] = self.document[section] + \
                        sent_tokenize(blk.text)
        except StopIteration:
            pass
        except Exception:
            print "Something went wrong!"
        for key, val in self.document.iteritems():
            print key
            print val


if __name__ == '__main__':
    Document('../demo/E06-1050.xml')
