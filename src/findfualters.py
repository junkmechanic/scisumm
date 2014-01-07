import subprocess
import os
import re

os.chdir('/home/ankur/devbench/scientific/support/SVM-light-TK/svm-light-TK-1.2.1')
#p = subprocess.Popen(['./svm_learn', '-t', '5', '../feature-trees.txt', '../model-temp1.txt'], stdout=subprocess.PIPE)
#out, err = p.communicate()
#if(re.search('ERROR:', out)):
#    print out

lines = []
num = 1
tot = 0
with open("../test-features.txt", 'r') as filein:
    lines = filein.readlines()
for l in lines:
    with open('../temp-feature.txt', 'w') as tfile:
        tfile.write(l)
    p = subprocess.Popen(['./svm_learn', '-t', '5', '../temp-feature.txt', '../tempmodel.txt'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    if(re.search('ERROR:', out)):
        print num
        tot += 1
    else:
        with open('../new-feature-trees.txt', 'a') as fileout:
            fileout.write(l)
    num += 1
print tot
