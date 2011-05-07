#!/usr/bin/python2

import os
import yaml
import shutil

from page import Page
import renderers

class Wok(object):
    default_options = {
        'content_dir' : 'content',
        'template_dir': 'templates',
        'output_dir'  : 'output',
        'media_dir'   : 'media',
        'site_title'  : 'Some random Wok site',
    }

    def __init__(self):
        self.all_pages = []

        self.read_options()
        self.prepare_output()
        self.load_pages()
        self.make_tree()
        self.render_site()

    def read_options(self):
        self.options = Wok.default_options.copy()

        if os.path.isfile('config'):
            with open('config') as f:
                yaml_config = yaml.load(f)

            if yaml_config:
                self.options.update(yaml_config)

    def prepare_output(self):
        if os.path.isdir(self.options['output_dir']):
            shutil.rmtree(self.options['output_dir'])
        os.mkdir(self.options['output_dir'])

        for name in os.listdir(self.options['media_dir']):
            path = os.path.join(self.options['media_dir'], name)
            if os.path.isdir(path):
                shutil.copytree(path, os.path.join(self.options['output_dir'],name), symlinks=True)
            else:
                shutil.copy(path, self.options['output_dir'])

    def load_pages(self):
        for root, dirs, files in os.walk(self.options['content_dir']):
            # Grab all the parsable files
            for f in files:
                ext = f.split('.')[-1]
                renderer = renderers.Plain

                for r in renderers.all:
                    if ext in r.extensions:
                        renderer = r

                self.all_pages.append(Page(os.path.join(root,f), self.options, renderer))

    def make_tree(self):
        site_tree = {}
        # We want to parse these in a approximately breadth first order
        self.all_pages.sort(key=lambda p: len(p.category))

        for p in self.all_pages:
            parent = site_tree
            for cat in p.category:
                assert(cat in parent)
                parent = parent[cat].subpages
            parent[p.title] = p

    def render_site(self):
        for p in self.all_pages:
            if p.published:
                p.render()
                p.write()

if __name__ == '__main__':
    Wok()
