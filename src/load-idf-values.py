import pickle

TF_IDF_values = {}
picklefile = "google-tf-idf-values.pickle"
with open(picklefile, 'rb') as pfile:
    IDF_values = pickle.load(pfile)
print "TF"
for key in IDF_values.keys():
    print "{} : {} {}".format(key, str(len(IDF_values[key].items())),
                              IDF_values[key])
