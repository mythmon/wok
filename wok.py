#!/usr/bin/python2

import sys
import os
import markdown
import re
import jinja2
import yaml
from unicodedata import normalize

import util

class Page(object):

    tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))

    def __init__(self, path):
        self.header = None
        self.original = None
        self.parsed = None
        self.meta = {}

        self.path = path
        dir, filename = os.path.split(path)

        with open(path) as f:
            self.original = f.read()
            splits = self.original.split('---')
            header = splits[0]
            self.original = splits[1]
            self.content = markdown.markdown(self.original)
            self.meta = yaml.load(header)

            if not 'title' in self.meta:
                self.meta['title'] = re.match(r'^(.*)\.mkd$', filename).group(1)
                util.out.warn('meta', 'You didn\'t specify a title, using the file name.')
            if not 'slug' in self.meta:
                self.meta['slug'] = util.slugify(self.meta['title'])
                util.out.debug('meta', 'You didn\'t specify a title, using the file name.')
            elif meta['slug'] != util.slugify(self.meta['slug']):
                util.out.warn('meta', 'Your slug should probably be all lower case, and match the regex "[a-z0-9-]*"')

        self.render()

    def render(self):
        type = self.meta.get('type', 'default')
        template = Page.tmpl_env.get_template(type + '.html')
        templ_vars = {
            'page': { 'content': self.content, }
        }
        templ_vars['page'].update(self.meta)
        self.html = template.render(templ_vars)

    def write(self, dir):
        filename = self.meta['slug'] + '.html'
        with open(os.path.join(dir, filename), 'w') as f:
            f.write(self.html)

def main():
    if not os.path.isdir('output'):
        os.mkdir('output')

    for root, dirs, files in os.walk('.'):
        # Grab all the markdown files
        for f in [f for f in files if f[-4:] == '.mkd']:
            p = Page(os.path.join(root,f))
            p.write('output')

if __name__ == '__main__':
    main()
