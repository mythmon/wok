#!/usr/bin/python2

import sys
import os
import markdown
import jinja2
import yaml
from collections import namedtuple
import re

import util

class Page(object):

    tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))

    def __init__(self, path):
        self.header = None
        self.original = None
        self.parsed = None
        self.meta = {}

        self.path = path
        _, self.filename = os.path.split(path)

        with open(path) as f:
            self.original = f.read()
            # Maximum of one split, so --- in the content doesn't get split.
            splits = self.original.split('---', 1)
            header = splits[0]
            self.original = splits[1]
            self.content = markdown.markdown(self.original)
            self.meta = yaml.load(header)

        self.build_meta()
        self.render()

    remove_mkd = re.compile(r'^(.*)\.mkd$')
    def build_meta(self):
        if not 'title' in self.meta:
            self.meta['title'] = remove_mkd.match(self.filename).group(1)
            util.out.warn('metadata',
                "You didn't specify a title in  {0}. Using the file name as a title."
                .format(self.filename))
        # Guranteed: title exists.

        if not 'slug' in self.meta:
            self.meta['slug'] = util.slugify(self.meta['title'])
            util.out.debug('metadata',
                'You didn\'t specify a slug, generating it from the title.')
        elif self.meta['slug'] != util.slugify(self.meta['slug']):
            util.out.warn('metadata',
                'Your slug should probably be all lower case,' +
                'and match the regex "[a-z0-9-]*"')
        # Guranteed: slug exists.

        Author = namedtuple('Author', ['raw', 'name', 'email'])
        if 'author' in self.meta:
            # Grab a name and maybe an email
            name, _, email = re.match(r'([^<>]*)( +<(.*@.*)>)$', self.meta['author']).groups()
            self.meta['author'] = Author(self.meta['author'], name, email)
        else:
            self.meta['author'] = Author(None, None, None)
        # Guranteed: author exists.


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
