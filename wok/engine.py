#!/usr/bin/python2
import os
import yaml
import shutil
from datetime import datetime
from optparse import OptionParser

import wok
from wok import page
from wok import renderers
from wok import util

class Engine(object):
    default_options = {
        'content_dir' : 'content',
        'template_dir': 'templates',
        'output_dir'  : 'output',
        'media_dir'   : 'media',
        'site_title'  : 'Some random Wok site',
    }

    def __init__(self, output_lvl = 1):

        parser = OptionParser(version='%prog v{0}'.format(wok.version))

        parser.set_defaults(verbose=1)
        parser.add_option('-q', '--quiet', action='store_const', const=0,
                dest='verbose')
        parser.add_option('--warnings', action='store_const', const=1,
                dest='verbose')
        parser.add_option('-v', '--verbose', action='store_const', const=2,
                dest='verbose')
        parser.add_option('--debug', action='store_const', const=3,
                dest='verbose')

        options, args = parser.parse_args()

        self.all_pages = []
        util.out.level = output_lvl

        self.read_options()
        self.prepare_output()
        self.load_pages()
        self.make_tree()
        self.render_site()

    def read_options(self):
        self.options = Engine.default_options.copy()

        if os.path.isfile('config'):
            with open('config') as f:
                yaml_config = yaml.load(f)

            if yaml_config:
                self.options.update(yaml_config)

    def prepare_output(self):
        if os.path.isdir(self.options['output_dir']):
            shutil.rmtree(self.options['output_dir'])
        os.mkdir(self.options['output_dir'])

        # Copy the media directory to the output folder
        try:
            for name in os.listdir(self.options['media_dir']):
                path = os.path.join(self.options['media_dir'], name)
                if os.path.isdir(path):
                    shutil.copytree(
                            path,
                            os.path.join(self.options['output_dir'], name), 
                            symlinks=True
                    )
                else:
                    shutil.copy(path, self.options['output_dir'])

        # Do nothing if the media directory doesn't exist
        except OSError:
            pass

    def load_pages(self):
        for root, dirs, files in os.walk(self.options['content_dir']):
            # Grab all the parsable files
            for f in files:
                # As long as the current file is not hidden, append it to the
                # page list
                if not f.startswith('.'):
                    ext = f.split('.')[-1]
                    renderer = renderers.Plain

                    for r in renderers.all:
                        if ext in r.extensions:
                            renderer = r

                    self.all_pages.append(
                        page.Page(os.path.join(root,f), self.options,
                            renderer))

    def make_tree(self):
        site_tree = []
        # We want to parse these in a approximately breadth first order
        self.all_pages.sort(key=lambda p: len(p.category))

        for p in self.all_pages:
            try:
                siblings = site_tree
                for cat in p.category:
                    parent = [subpage for subpage in siblings
                                 if subpage.slug == cat][0]
                    siblings = parent.subpages
                siblings.append(p)
            except IndexError:
                util.out.error('Categories',
                    'It looks like the page "{0}" is an orphan!  For a page '
                    'to be in category "foo/bar", there needs to be page with '
                    'slug "foo" with no category, and a page with slug "bar" '
                    'with category "foo".'.format(p.path))

    def render_site(self):
        # Gather tags
        tag_set = set()
        for p in self.all_pages:
            tag_set = tag_set.union(p.tags)
        tag_dict = dict()
        for tag in tag_set:
            tag_dict[tag] = [p for p in self.all_pages if tag in p.tags]

        templ_vars = {
            'site': {
                'title': self.options.get('site_title', 'Untitled'),
                'datetime': datetime.now(),
                'tags': tag_dict,
                'pages': self.all_pages,
            },
        }

        for p in self.all_pages:
            if p.published:
                p.render(templ_vars)
                p.write()

if __name__ == '__main__':
    Engine()
