import string
import pickle
import re

idffile = "words.IDF"
#idffile = "idf/xaa"
picklefile = "google-tf-idf-values.pickle"

IDF_values = {}

with open(idffile, 'r') as ifile:
    for line in ifile.readlines():
        reg = re.match(r'([a-zA-Z]+)\s+([\d+\.]+)', line.strip())
        if reg is None:
            print "Couldnt parse : " + line.strip()
        else:
            word = reg.group(1).lower()
            idfval = reg.group(2)
            if word[0] not in string.lowercase:
                continue
            else:
                if word[0] not in IDF_values.keys():
                    IDF_values[word[0]] = {}
                IDF_values[word[0]][word] = idfval

#for key in IDF_values.keys():
#    print "{} : {}".format(key, str(len(IDF_values[key].items())))
#print IDF_values

with open(picklefile, 'wb') as pfile:
    pickle.dump(IDF_values, pfile)
