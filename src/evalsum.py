from PythonROUGE import PythonROUGE
from Config import DIR

#summary_type = '-svm_summary.txt'
summary_type = '-a.txt'
guess_list = ['C08-1122', 'P07-3014', 'W11-2821']
#guess_list = ['C08', 'P07', ' W11']
ref_list = [['C08-1122-Ref1.txt', 'C08-1122-Ref2.txt', 'C08-1122-Ref3.txt',
             'C08-1122-Ref4.txt', 'C08-1122-Ref5.txt'],
            ['P07-3014-Ref1.txt', 'P07-3014-Ref2.txt', 'P07-3014-Ref3.txt',
             'P07-3014-Ref4.txt', 'P07-3014-Ref5.txt'],
            ['W11-2821-Ref2.txt', 'W11-2821-Ref3.txt', 'W11-2821-Ref4.txt'],
            ]
            #['W93-0225-Ref2.txt']]
guess_summary_list = []
for item in guess_list:
    guess_summary_list.append(DIR['DATA'] + item + summary_type)
ref_summary_list = []
for refsum in ref_list:
    ref_temp = []
    for item in refsum:
        ref_temp.append(DIR['DATA'] + item)
    ref_summary_list.append(ref_temp)
recall, precision, F_measure = PythonROUGE(guess_summary_list,
                                           ref_summary_list,
                                           ngram_order=2)

print recall, precision, F_measure
