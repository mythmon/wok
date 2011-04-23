#!/usr/bin/python2

import os
import yaml
import shutil

from page import Page

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
        print(path)
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(options['output_dir'],name), symlinks=True)
        else:
            shutil.copy(path, options['output_dir'])

    for root, dirs, files in os.walk(options['content_dir']):
        # Grab all the markdown files
        for f in [f for f in files if f[-4:] == '.mkd']:
            p = Page(os.path.join(root,f), options)
            p.render()
            if p.meta['published']:
                p.write()

if __name__ == '__main__':
    main()
