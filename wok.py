#!/usr/bin/python2

import sys
import os
import markdown
import re

all_pages = []

class Page(object):
    def __init__(self, path):
        self.original = None
        self.parsed = None

        self.path, self.filename = os.path.split(path)
        self.name = re.match(r'^(.*)\.mkd$', self.filename).group(1)

        with open(path) as f:
            self.original = f.read()
            self.parsed = markdown.markdown(self.original)

    def writeToFile(self, path = None):
        if path == None:
            path = os.path.join(self.path, self.name + '.html')
        with open(path, 'w') as f:
            f.write(self.parsed)

def main():
    all_pages = []

    for root, dirs, files in os.walk('.'):
        # Grab all the markdown files
        for f in [f for f in files if f[-4:] == '.mkd']:
            p = Page(os.path.join(root,f))
            all_pages.append(p)
            p.writeToFile()

if __name__ == '__main__':
    main()
