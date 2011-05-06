#!/usr/bin/python2

import os
import yaml
import shutil

from page import Page
import renderers

options_defaults = {
    'content_dir' : 'content',
    'template_dir': 'template',
    'output_dir'  : 'output',
    'media_dir'   : 'output',
    'site_name'   : 'Some random Wok site',
}

def main():
    options = options_defaults.copy()
    if os.path.isfile('config'):
        with open('config') as f:
            yaml_config = yaml.load(f)

        if yaml_config:
            options.update(yaml_config)

    if os.path.isdir(options['output_dir']):
        shutil.rmtree(options['output_dir'])
    os.mkdir(options['output_dir'])

    for name in os.listdir(options['media_dir']):
        path = os.path.join(options['media_dir'], name)
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(options['output_dir'],name), symlinks=True)
        else:
            shutil.copy(path, options['output_dir'])

    site_pages = []

    for root, dirs, files in os.walk(options['content_dir']):
        # Grab all the parsable files
        for f in files:
            ext = f.split('.')[-1]
            renderer = renderers.Plain

            for r in renderers.all:
                if ext in r.extensions:
                    renderer = r

            site_pages.append(Page(os.path.join(root,f), options, renderer))

    site_tree = {}
    site_pages.sort(key=lambda p: len(p.meta['category']))
    for p in site_pages:
        parent = site_tree
        for cat in p.meta['category']:
            assert(cat in parent)
            parent = parent[cat].subpages
        parent[p.meta['title']] = p

    for p in site_pages:
        p.render()

        if p.meta['published']:
            p.write()

if __name__ == '__main__':
    main()
