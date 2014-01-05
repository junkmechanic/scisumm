from Document import Document
from Config import DIR
from glob import glob
import os


def getAbstracts():
    dir = DIR['BASE'] + "demo/"
    os.chdir(dir)
    samples = ''
    for file in glob("*.xml"):
        doc = Document(file)
        sent, offset = doc.section_sentences('abstract')
        samples += '\n'.join(sent)
    # for now this is the location of the file
    with open(DIR['BASE'] + 'data/summary_sentences.txt', 'w') as file:
        file.write(samples)


if __name__ == '__main__':
    getAbstracts()
