#!/usr/bin/python2

import os
from page import Page

def main():
    if not os.path.isdir('output'):
        os.mkdir('output')

    for root, dirs, files in os.walk('.'):
        # Grab all the markdown files
        for f in [f for f in files if f[-4:] == '.mkd']:
            p = Page(os.path.join(root,f))
            p.render()
            p.write('./output')

if __name__ == '__main__':
    main()
