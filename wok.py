#!/usr/bin/python2

import sys
import os
import markdown
import re
import jinja2
import yaml

tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))

class Page(object):

    def __init__(self, path):
        self.header = None
        self.original = None
        self.parsed = None
        self.meta = {}

        self.path = path
        dir, filename = os.path.split(path)
        self.name = re.match(r'^(.*)\.mkd$', filename).group(1)

        with open(path) as f:
            self.original = f.read()
            splits = self.original.split('---')
            header = splits[0]
            self.original = splits[1]
            self.content = markdown.markdown(self.original)
            self.meta = yaml.load(header)

        self.render()

    def render(self):
        type = self.meta.get('type', 'default')
        template = tmpl_env.get_template(type + '.html')
        templ_vars = {
            'page': {
                'content': self.content,
                'title': self.meta['title'],
            }
        }
        self.html = template.render(templ_vars)

    def write(self, dir, filename=None):
        if filename == None:
            filename = self.name + '.html'
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
