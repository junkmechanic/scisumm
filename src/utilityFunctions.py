# This script contains all the functions that are independent of the project
# specific libraries.

import subprocess
import os
from Config import DIR


def writeToFile(outfile, txt, mode='a'):
    with open(outfile, mode) as file:
        file.write(txt)


def deleteFiles(flist):
    for file in flist:
        if os.path.isfile(file):
            d, f = os.path.split(file)
            print f + " exists. Deleting.."
            os.remove(file)


def trainSvm(featurefile, modelfile, gamma=1):
    learn = DIR['BASE'] + "lib/svm-light/svm_learn"
    subprocess.call([learn, '-t', '2', '-x', '1', '-g', str(gamma),
                     featurefile, modelfile])


def predictSvm(featurefile, model, outfile):
    classify = DIR['BASE'] + "lib/svm-light/svm_classify"
    subprocess.call([classify, featurefile, model, outfile])
