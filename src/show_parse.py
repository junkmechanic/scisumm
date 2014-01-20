import subprocess
#import os
import sys
import argparse

# TODO: Change to the directory where the class file is


def main(args):
    infile = "../temp-todisplay.txt"
    flag = 'w'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help="input file with sentences")
    parser.add_argument('-s', '--sent', help="sentences in command line",
                        action="append")
    args = parser.parse_args()
    if args.file:
        infile = args.file
        flag = 'a'
    if args.sent:
        with open(infile, flag) as ofile:
            ofile.write('\n'.join(args.sent))
            ofile.write('\n')
    subprocess.call(['java', '-cp', '.:./*', 'ParsedTree', '--display',
                     infile])


if __name__ == '__main__':
    main(sys.argv[1:])
