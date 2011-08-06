import os
from collections import namedtuple
from datetime import datetime
import logging

import jinja2
import yaml
import re

from wok import util
from wok import renderers

class Page(object):
    """
    A single page on the website in all it's form, as well as it's
    associated metadata.
    """

    def __init__(self, path, options, renderer=None, extra_meta=None):
        """
        Load a file from disk, and parse the metadata from it.

        Note that you still need to call `render` and `write` to do anything
        interesting.
        """
        self.header = None
        self.original = None
        self.parsed = None
        self.options = options
        self.renderer = renderer if renderer else renderers.Plain

        # TODO: It's not good to make a new environment every time, but we if
        # we pass the options in each time, its possible it will change per
        # instance. Fix this.
        self.tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
            self.options.get('template_dir', 'templates')))

        self.path = path
        _, self.filename = os.path.split(path)

        with open(path) as f:
            self.original = f.read()
            # Maximum of one split, so --- in the content doesn't get split.
            splits = self.original.split('---', 1)

            # Handle the case where no meta data was provided
            if len(splits) == 1:
                self.original = splits[0]
            else:
                header = splits[0]
                self.original = splits[1]
                self.meta = yaml.load(header)

        if extra_meta:
            logging.debug('Got extra_meta')
            self.meta.update(extra_meta)

        self.build_meta()
        logging.info('Rendering {0} with {1} (pagination? {2})'.format(
            self.meta['slug'], self.renderer, 'pagination' in self.meta))
        self.meta['content'] = self.renderer.render(self.original)

    def build_meta(self):
        """
        Ensures the guarantees about metadata for documents are valid.

        `page.title` - will exist and will be a string.
        `page.slug` - will exist and will be a string.
        `page.author` - will exist, and contain fields `name` and `email`.
        `page.category` - will be a list.
        `page.published` - will exist.
        `page.datetime` - will be a datetime.
        `page.tags` - will be a list.
        `page.url` - will be the url of the page, relative to the web root.
        `page.subpages` - will be a list containing every sub page of this page
        """

        if not self.meta:
            self.meta = {}

        # title
        if not 'title' in self.meta:
            self.meta['title'] = '.'.join(self.filename.split('.')[:-1])
            if (self.meta['title'] == ''):
                self.meta['title'] = self.filename

            logging.warning("You didn't specify a title in {0}. "
                    "Using the file name as a title.".format(self.filename))

        # slug
        if not 'slug' in self.meta:
            self.meta['slug'] = util.slugify(self.meta['title'])
            logging.debug("You didn't specify a slug, generating it from the title.")
        elif self.meta['slug'] != util.slugify(self.meta['slug']):
            logging.warning('Your slug should probably be all lower case, and '
                'match "[a-z0-9-]*"')

        # author
        if 'author' in self.meta:
            self.meta['author'] = Author.parse(self.meta['author'])
        elif 'author' in self.options:
            self.meta['author'] = self.options['author']
        else:
            self.meta['author'] = Author()

        # category
        if 'category' in self.meta:
            self.meta['category'] = self.meta['category'].split('/')
        else:
            self.meta['category'] = []
        if self.meta['category'] == None:
            self.meta = []

        # published
        if not 'published' in self.meta:
            self.meta['published'] = True

        # datetime
        for name in ['time', 'date']:
            if name in self.meta:
                self.meta['datetime'] = self.meta[name]
        if not 'datetime' in self.meta:
            self.meta['datetime'] = datetime.now()

        # tags
        if not 'tags' in self.meta:
            self.meta['tags'] = []
        else:
            self.meta['tags'] = [t.strip() for t in
                    self.meta['tags'].split(',')]

        logging.debug('Tags for {0}: {1}'.
                format(self.meta['slug'], self.meta['tags']))

        # pagination
        if 'pagination' not in self.meta:
            self.meta['pagination'] = {}

        if 'cur_page' not in self.meta['pagination']:
            self.meta['pagination']['cur_page'] = 1
        if 'num_pages' not in self.meta['pagination']:
            self.meta['pagination']['num_pages'] = 1

        # url
        parts = {
            'slug': self.meta['slug'],
            'category': '/'.join(self.meta['category']),
            'page': self.meta['pagination']['cur_page'],
        }
        logging.debug('current page: ' + repr(parts['page']))
        if parts['page'] == 1:
            parts['page'] = ''

        if not 'url' in self.meta:
            self.meta['url'] = self.options['url_pattern'].format(**parts);
        else:
            self.meta['url'] = self.meta['url'].format(**parts);
        # Get rid of extra slashes
        self.meta['url'] = re.sub(r'//+', '/', self.meta['url'])
        logging.debug(self.meta['url'])

        # subpages
        self.meta['subpages'] = []

    def render(self, templ_vars=None):
        """
        Renders the page to full html with the template engine.
        """
        type = self.meta.get('type', 'default')
        template = self.tmpl_env.get_template(type + '.html')

        if not templ_vars:
            templ_vars = {}

        extra_pages = []
        if 'pagination' in self.meta and 'list' in self.meta['pagination']:
            if 'page_items' not in self.meta['pagination']:
                # This is the first page of a set of pages. Set up the rest

                source = self.meta['subpages']
                # for now we assume they meant `page.subpages`

                source.sort(key=lambda x: x['slug'])
                chunks = list(util.chunk(source, self.meta['pagination']['limit']))

                for idx, chunk in enumerate(chunks[1:]):
                    print('chunk is ' + repr([c['slug'] for c in chunk]))
                    logging.debug('idx: ' + repr(idx))
                    extra_meta = {
                        'pagination': {
                            'page_items': chunk,
                            'num_pages': len(chunks),
                            'cur_page': idx + 2,
                        }
                    }
                    new_page = Page(self.path, self.options,
                        renderer=self.renderer, extra_meta=extra_meta)
                    extra_pages.append(new_page)

                for idx, page in enumerate(extra_pages):
                    if idx == 0:
                        page.meta['pagination']['prev_page'] = self.meta
                    else:
                        page.meta['pagination']['prev_page'] = extra_pages[idx-1].meta

                    if idx < len(extra_pages) - 1:
                        page.meta['pagination']['next_page'] = extra_pages[idx+1].meta

                self.meta['pagination'].update({
                    'page_items': chunks[0],
                    'num_pages': len(chunks),
                    'cur_page': 1,
                    'next_page': extra_pages[0].meta,
                })
            else:
                pass
                # Not page 1, render normally.

        if 'page' in templ_vars:
            logging.debug('Found defaulted page data.')
            templ_vars['page'].update(self.meta)
        else:
            templ_vars.update({
                'page': self.meta,
                'pagination': self.meta['pagination'],
            })

        self.html = template.render(templ_vars)

        logging.debug('extra pages is: ' + repr(extra_pages))
        return extra_pages

    def write(self):
        """Write the page to an html file on disk."""

        # Use what we are passed, or the default given, or the current dir
        path = self.options.get('output_dir', '.')
        path += self.meta['url']

        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            logging.debug('makedirs failed for {0}'.format(
                os.path.basename(path)))
            # Probably that the dir already exists, so thats ok.
            # TODO: double check this. Permission errors are something to worry
            # about
        logging.info('writing to {0}'.format(path))

        f = open(path, 'w')
        f.write(self.html)
        f.close()

    def __repr__(self):
        return "&lt;wok.page.Page '{0}'&gt;".format(self.meta['slug'])


class Author(object):
    """Smartly manages a author with name and email"""
    parse_author_regex = re.compile(r'^([^<>]*) *(<(.*@.*)>)?$')

    def __init__(self, raw='', name=None, email=None):
        self.raw = raw.strip()
        self.name = name
        self.email = email

    @classmethod
    def parse(cls, raw):
        a = cls(raw)
        a.name, _, a.email = cls.parse_author_regex.match(raw).groups()
        if a.name:
            a.name = a.name.strip()
        if a.email:
            a.email = a.email.strip()
        return a

    def __str__(self):
        if not self.name:
            return self.raw
        if not self.email:
            return self.name

        return "{0} <{1}>".format(self.name, self.email)

