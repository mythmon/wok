# System
import os
import sys
from collections import namedtuple
from datetime import datetime, date, time
import logging

# Libraries
import jinja2
import yaml
import re

# Wok
from wok import util
from wok import renderers
from wok.jinja import GlobFileLoader, AmbiguousTemplate

class Page(object):
    """
    A single page on the website in all it's form (raw, rendered, templated) ,
    as well as it's associated metadata.
    """

    tmpl_env = None

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

        logging.info('Loading {0}'.format(os.path.basename(path)))

        if Page.tmpl_env is None:
            Page.tmpl_env = jinja2.Environment(loader=GlobFileLoader(
                self.options.get('template_dir', 'templates')))

        self.path = path
        _, self.filename = os.path.split(path)

        with open(path) as f:
            self.original = f.read()
            splits = self.original.split('\n---\n')

            if len(splits) > 3:
                logging.warning('Found more --- delimited sections in {0} '
                                'than expected. Squashing the extra together.'
                                .format(self.path))

            # Handle the case where no meta data was provided
            if len(splits) == 1:
                self.original = splits[0]
                self.meta = {}

            elif len(splits) == 2:
                header = splits[0]
                self.meta = yaml.load(header)
                self.original = splits[1]

            elif len(splits) == 3:
                header = splits[0]
                self.meta = {}
                self.original = '\n'.join(splits[1:])
                self.meta['preview'] = splits[1]
                self.meta.update(yaml.load(header))
                logging.debug('Got preview')

        if extra_meta:
            logging.debug('Got extra_meta')
            self.meta.update(extra_meta)

        self.build_meta()
        self.meta['content'] = self.renderer.render(self.original)

    def build_meta(self):
        """
        Ensures the guarantees about metadata for documents are valid.

        `page.title` - Will be a string.
        `page.slug` - Will be a string.
        `page.author` - Will have fields `name` and `email`.
        `page.authors` - Will be a list of Authors.
        `page.category` - Will be a list.
        `page.published` - Will exist.
        `page.datetime` - Will be a datetime, or None.
        `page.date` - Will be a date, or None.
        `page.time` - Will be a time, or None.
        `page.tags` - Will be a list.
        `page.url` - Will be the url of the page, relative to the web root.
        `page.subpages` - Will be a list containing every sub page of this page
        """

        if not self.meta:
            self.meta = {}

        # title
        if not 'title' in self.meta:
            self.meta['title'] = '.'.join(self.filename.split('.')[:-1])
            if (self.meta['title'] == ''):
                self.meta['title'] = self.filename

            logging.info("You didn't specify a title in {0}. "
                    "Using the file name as a title.".format(self.filename))

        # slug
        if not 'slug' in self.meta:
            self.meta['slug'] = util.slugify(self.meta['title'])
            logging.debug("You didn't specify a slug, generating it from the title.")
        elif self.meta['slug'] != util.slugify(self.meta['slug']):
            logging.warning('Your slug should probably be all lower case, and '
                'match "[a-z0-9-]*"')

        # authors and author
        authors = self.meta.get('authors', self.meta.get('author', None))
        if isinstance(authors, list):
            self.meta['authors'] = [Author.parse(a) for a in authors]
        elif isinstance(authors, str):
            self.meta['authors'] = [Author.parse(a) for a in authors.split(',')]
            if len(self.meta['authors']) > 1:
                logging.warn('Deprecation Warning: Use YAML lists instead of '
                        'CSV for multiple authors. i.e. ["John Doe", "Jane '
                        'Smith"] instead of "John Doe, Jane Smith". In '
                        '{0}.'.format(self.path))

        elif authors is None:
            if 'authors' in self.options:
                self.meta['authors'] = self.options['authors']
            else:
                self.meta['authors'] = []
        else:
            # wait, what?
            self.meta['authors'] = []
            logging.error(('Authors in {0} is an unknown type. Valid types '
                           'are string or list.').format(self.path))

        if self.meta['authors']:
            self.meta['author'] = self.meta['authors']
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

        # make_file
        if not 'make_file' in self.meta:
            self.meta['make_file'] = True

        # datetime, date, time
        util.date_and_times(self.meta)

        # tags
        if 'tags' in self.meta:
            if isinstance(self.meta['tags'], list):
                # good
                pass
            elif isinstance(self.meta['tags'], str):
                self.meta['tags'] = [t.strip() for t in
                    self.meta['tags'].split(',')]
                if len(self.meta['tags']) > 1:
                    logging.warn('Deprecation Warning: Use YAML lists instead '
                            'of CSV for multiple tags. i.e. tags: [guide, '
                            'howto] instead of tags: guide, howto. In {0}.'
                            .format(self.path))
        else:
            self.meta['tags'] = []

        logging.debug('Tags for {0}: {1}'.
                format(self.meta['slug'], self.meta['tags']))

        # pagination
        if 'pagination' not in self.meta:
            self.meta['pagination'] = {}

        if 'cur_page' not in self.meta['pagination']:
            self.meta['pagination']['cur_page'] = 1
        if 'num_pages' not in self.meta['pagination']:
            self.meta['pagination']['num_pages'] = 1

        # template
        try:
            template_type = self.meta.get('type', 'default')
            self.template = Page.tmpl_env.get_template(template_type + '.*')
        except jinja2.loaders.TemplateNotFound:
            logging.error('No template "{0}.*" found in template directory. Aborting.'
                    .format(template_type))
            sys.exit()
        except AmbiguousTemplate:
            logging.error(('Ambiguous template found. There are two files that '
                          'match "{0}.*". Aborting.').format(template_type))
            sys.exit()

        # url
        parts = {
            'slug': self.meta['slug'],
            'category': '/'.join(self.meta['category']),
            'page': self.meta['pagination']['cur_page'],
        }
        logging.debug('current page: ' + repr(parts['page']))

        # Pull extensions from the template's real file name.
        match = re.match('.*/[^\.]*\.(.*)$', self.template.filename)
        if match:
            parts['ext'] = match.groups()[0]
        else:
            parts['ext'] = ''
        # Deprecated
        parts['type'] = parts['ext']
        self.meta['ext'] = parts['ext']

        if parts['page'] == 1:
            parts['page'] = ''

        if not 'url' in self.meta:
            self.meta['url'] = self.options['url_pattern'].format(**parts);
        else:
            self.meta['url'] = self.meta['url'].format(**parts);
        # Get rid of extra slashes
        self.meta['url'] = re.sub(r'//+', '/', self.meta['url'])
        logging.debug(self.meta['url'])
        # If we have been asked to, rip out any plain "index.html"s
        if not self.options['url_include_index']:
            self.meta['url'] = re.sub(r'/index\.html$', '/', self.meta['url'])

        # subpages
        self.meta['subpages'] = []

    def render(self, templ_vars=None):
        """
        Renders the page with the template engine.
        """
        if not templ_vars:
            templ_vars = {}

        if 'pagination' in self.meta and 'list' in self.meta['pagination']:
            extra_pages = self.paginate()
        else:
            extra_pages = []

        if 'page' in templ_vars:
            logging.debug('Found defaulted page data.')
            templ_vars['page'].update(self.meta)
        else:
            templ_vars['page'] = self.meta

        if 'pagination' in templ_vars:
            templ_vars['pagination'].update(self.meta['pagination'])
        else:
            templ_vars['pagination'] = self.meta['pagination']

        logging.debug('templ_vars.keys(): ' + repr(templ_vars.keys()))
        self.rendered = self.template.render(templ_vars)

        logging.debug('extra pages is: ' + repr(extra_pages))
        return extra_pages

    def paginate(self):
        extra_pages = []
        if 'page_items' not in self.meta['pagination']:
            # This is the first page of a set of pages. Set up the rest. Other
            # wise don't do anything.

            source_spec = self.meta['pagination']['list'].split('.')
            logging.debug('pagination source is: ' + repr(source_spec))

            if source_spec[0] == 'page':
                source = self.meta
                source_spec.pop(0)
            elif source_spec[0] == 'site':
                source = templ_vars['site']
                source_spec.pop(0)
            else:
                logging.error('Unknown pagination source! Not paginating')
                return

            for k in source_spec:
                logging.debug(k)
                source = source[k]

            sort_key = self.meta['pagination'].get('sort_key', None)
            sort_reverse = self.meta['pagination'].get('sort_reverse', False)

            logging.debug('sort_key: {0}, sort_reverse: {1}'.format(
                sort_key, sort_reverse))

            if isinstance(source[0], Page):
                source = [p.meta for p in source]

            if sort_key is not None:
                if isinstance(source[0], dict):
                    source.sort(key=lambda x: x[sort_key],
                            reverse=sort_reverse)
                else:
                    source.sort(key=lambda x: x.__getattribute__(sort_key),
                            reverse=sort_reverse)

            chunks = list(util.chunk(source, self.meta['pagination']['limit']))

            # Make a page for each chunk
            for idx, chunk in enumerate(chunks[1:]):
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

            # Set up the next/previous page links
            for idx, page in enumerate(extra_pages):
                if idx == 0:
                    page.meta['pagination']['prev_page'] = self.meta
                else:
                    page.meta['pagination']['prev_page'] = extra_pages[idx-1].meta

                if idx < len(extra_pages) - 1:
                    page.meta['pagination']['next_page'] = extra_pages[idx+1].meta
                else:
                    page.meta['pagination']['next_page'] = None

            # Pagination date for this page
            self.meta['pagination'].update({
                'page_items': chunks[0],
                'num_pages': len(chunks),
                'cur_page': 1,
            })
            if len(extra_pages) > 1:
                self.meta['pagination']['next_page'] = extra_pages[0].meta

        return extra_pages

    def write(self):
        """Write the page to a rendered file on disk."""

        # Use what we are passed, or the default given, or the current dir
        path = self.options.get('output_dir', '.')
        path += self.meta['url']
        if path.endswith('/'):
            path += 'index.' + self.meta['ext']

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
        f.write(self.rendered)
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

    def __repr__(self):
        return '<wok.page.Author "{0} <{1}>">'.format(self.name, self.email)

    def __unicode__(self):
        s = self.__str__()
        return s.replace('<', '&lt;').replace('>', '&gt;')
