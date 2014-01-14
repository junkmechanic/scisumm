import subprocess
#import os
import sys

# TODO: Change to the directory where the class file is


def main(args):
    outfile = "../temp-todisplay.txt"
    with open(outfile) as ofile:
        sentences = []
        for blk in args:
            sentences.extend(blk.split('\n'))
        ofile.write('\n'.join(sentences))
    subprocess.call(['java', '-cp', '.:./*', 'ParsedTree', '--display',
                     '../temp-todisplay.txt'])


if __name__ == '__main__':
    main(sys.argv[1:])
