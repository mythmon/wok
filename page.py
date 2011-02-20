import os
from markdown import markdown
import jinja2
import yaml
from collections import namedtuple
import re
from datetime import datetime

import util

class Page(object):
    """A single page on the website in all it's form, as well as it's associated metadata."""

    tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
    Author = namedtuple('Author', ['raw', 'name', 'email'])
    remove_mkd_re = re.compile(r'^(.*)\.mkd$')
    parse_author_re = re.compile(r'([^<>]*)( +<(.*@.*)>)$')

    def __init__(self, path):
        """
        Load a file from disk, and parse the metadata from it.

        Note that you still need to call `render` and `write` to do anything
        interesting.
        """
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
            self.meta = yaml.load(header)

        self.build_meta()

    def build_meta(self):
        """
        Ensures the gurantees about metadata for documents are valid.

        `page.title` - will exist.
        `page.slug` - will exist.
        `page.author` - will exist, and contain fields `name` and `email`.
        `page.category` - will exist, and be a list.
        """

        if not 'title' in self.meta:
            self.meta['title'] = remove_mkd_re.match(self.filename).group(1)
            util.out.warn('metadata',
                "You didn't specify a title in  {0}. Using the file name as a title."
                .format(self.filename))
        # Gurantee: title exists.

        if not 'slug' in self.meta:
            self.meta['slug'] = util.slugify(self.meta['title'])
            util.out.debug('metadata',
                'You didn\'t specify a slug, generating it from the title.')
        elif self.meta['slug'] != util.slugify(self.meta['slug']):
            util.out.warn('metadata',
                'Your slug should probably be all lower case,' +
                'and match the regex "[a-z0-9-]*"')
        # Gurantee: slug exists.

        if 'author' in self.meta:
            # Grab a name and maybe an email
            name, _, email = Page.parse_author_re.match(self.meta['author']).groups()
            self.meta['author'] = Page.Author(self.meta['author'], name, email)
        else:
            self.meta['author'] = Page.Author(None, None, None)
        # Gurantee: author exists.

        if 'category' in self.meta:
            self.meta['category'] = self.meta['category'].split('/')
        else:
            self.meta['category'] = []
        # Gurantee: category exists

    def render(self):
        """
        Renders the page to full html.

        First parse the markdown to html, then build a set of variables for the
        template, finally render it with jinja2.
        """

        self.content = markdown(self.original, ['def_list', 'footnotes'])

        type = self.meta.get('type', 'default')
        template = Page.tmpl_env.get_template(type + '.html')
        templ_vars = {
            'page': { 'content': self.content, },
            'site': {
                'title': "Ahblah! Site Title!",
                'datetime': datetime.now(),
            }
        }
        templ_vars['page'].update(self.meta)
        self.html = template.render(templ_vars)

    def write(self, dir):
        """Write the page to an html file on disk."""
        filename = self.meta['slug'] + '.html'
        with open(os.path.join(dir, filename), 'w') as f:
            f.write(self.html)
