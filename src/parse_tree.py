import re


class Node:
    def __init__(self, str):
        reg = re.match(r'(\d)-\>([A-Za-z]+)-([A-Z\$]+)\s\(([a-z_]+)\)', str)
        if reg is None:
            print str
            print "Some fatal error. String not in expected format."
        else:
            self.level = int(reg.group(1))
            self.word = reg.group(2)
            self.pos = reg.group(3)
            self.dep = reg.group(4)
            self.children = []

    def append(self, node):
        self.children.append(node)

    def __str__(self):
        return (' ' * self.level * 2 + str(self.level) + '->' +
                self.word + '-' + self.pos + '-' + self.dep)


def parseTrees(infile):
    current = dict()
    with open(infile, 'r') as file:
        #import pdb; pdb.set_trace()
        for line in file.readlines():
            if len(line.strip()) == 0:
                processTree(current[0])
                current = dict()
            else:
                node = Node(line.strip())
                parent_level = node.level - 1
                if parent_level in current.keys():
                    current[parent_level].append(node)
                elif node.level == 0:
                    current[0] = node
                else:
                    print "Fatal error: parent level does not exist."
                current[node.level] = node


def processTree(root):
    printTree(root)


def printTree(root):
    print root
    printChildTree(root)


def printChildTree(node):
    for child in node.children:
        print child
        printChildTree(child)


if __name__ == '__main__':
    parseTrees('temp-display.txt')
