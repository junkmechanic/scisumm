from Document import Document
from Config import DIR
from glob import glob
from operator import itemgetter
from Ranker import TextRank
import os


# This is programmed to look for xml files processed by ParsCit in the demo
# directory present in the base directory of this repository. It will take all
# these files and output a file in the data directory that would contain
# abstracts from all the xml files.
def getAbstracts(outfile):
    dir = DIR['BASE'] + "demo/"
    os.chdir(dir)
    samples = ''
    total = 0
    for file in glob("*.xml"):
        try:
            doc = Document(file)
            sent, offset = doc.section_sentences('abstract')
            samples += '\n'.join(sent)
            print(file + " : Done")
            total += 1
        except Exception as e:
            print(file + str(e))
    # for now this is the location of the file
    writeToFile(outfile, samples, 'w')
    print ("Total number of files processed successfully : " + str(total))


def writeToFile(outfile, txt, mode='a'):
    with open(outfile, mode) as file:
        file.write(txt)


def preProcess(infile, outfile):
    with open(infile, 'r') as file:
        for line in file.readlines():
            if (len(line.split()) > 4):
                writeToFile(outfile, line, 'a')
    print("Short sentences removed.")
    # More preprocessing steps can be added here
    print("Preprocessing Done.")


# This is similar to getAbstracts in that it will look for ParsCit processed
# xml files in demo directory. It will then pick the sentences that rank the
# lowest in their TextRank values and put them all in a file together.
# Currently it will just take the 'num' lowest ranked sentences from each file.
def getUnwanted(outfile):
    dir = DIR['BASE'] + "demo/"
    os.chdir(dir)
    samples = ''
    total = 0
    num = 12
    samples = ''
    for file in glob("*.xml"):
        try:
            doc = Document(file)
            sentences, offset = doc.all_sentences()
            # Ranker
            ranker = TextRank(sentences)
            ranker.rank()
            scores = sorted(ranker.scores, key=itemgetter(1))
            for x in range(num):
                idx = scores[x][0] + offset
                samples += doc[idx].sentence.encode('utf-8') + '\n'
            total += 1
            print(file + " : Done")
        except Exception as e:
            print(file + str(e))
    # for now this is the location of the file
    writeToFile(outfile, samples, 'w')
    print ("Total number of files processed successfully : " + str(total))


if __name__ == '__main__':
    # for positive samples
    infile = DIR['BASE'] + 'data/summary_sentences.txt'
    outfile = DIR['BASE'] + 'data/pos-training-sent.txt'
    getAbstracts(infile)
    preProcess(infile, outfile)
    # for negative samples
    infile = DIR['BASE'] + 'data/unwanted_sentences.txt'
    outfile = DIR['BASE'] + 'data/neg-training-sent.txt'
    getUnwanted(infile)
    preProcess(infile, outfile)
