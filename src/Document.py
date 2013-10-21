from lxml import etree
import nltk


class Document:

    def __init__(self, xmlfile):
        tree = etree.parse(xmlfile)
        algrthms = tree.getroot()
        for section in algrthms.iterdescendants(['sectionHeader', 'bodyText']):
            print(section.text)


if __name__ == '__main__':
    Document('../demo/E06-1050.xml')
