#!/usr/bin/python2
import os
import sys
import shutil
from datetime import datetime
from optparse import OptionParser, OptionGroup
import logging

import yaml

import wok
from wok.page import Page, Author
from wok import renderers
from wok import util
from wok.dev_server import dev_server


class Engine(object):
    """
    The main engine of wok. Upon initialization, it generates a site from the
    source files.
    """
    default_options = {
        'content_dir': 'content',
        'template_dir': 'templates',
        'output_dir': 'output',
        'media_dir': 'media',
        'site_title': 'Some random Wok site',
        'url_pattern': '/{category}/{slug}{page}.{ext}',
        'url_include_index': True,
        'relative_urls': False,
    }
    SITE_ROOT = os.getcwd()

    def __init__(self, output_lvl=1):
        """
        Set up CLI options, logging levels, and start everything off.
        Afterwards, run a dev server if asked to.
        """

        # CLI options
        # -----------
        parser = OptionParser(version='%prog v{0}'.format(wok.version))

        # Add option to to run the development server after generating pages
        devserver_grp = OptionGroup(parser, "Development server",
                "Runs a small development server after site generation. "
                "--address and --port will be ignored if --server is absent.")
        devserver_grp.add_option('--server', action='store_true',
                dest='runserver',
                help="run a development server after generating the site")
        devserver_grp.add_option('--address', action='store', dest='address',
                help="specify ADDRESS on which to run development server")
        devserver_grp.add_option('--port', action='store', dest='port',
                type='int',
                help="specify PORT on which to run development server")
        parser.add_option_group(devserver_grp)

        # Options for noisiness level and logging
        logging_grp = OptionGroup(parser, "Logging",
                "By default, log messages will be sent to standard out, "
                "and report only errors and warnings.")
        parser.set_defaults(loglevel=logging.WARNING)
        logging_grp.add_option('-q', '--quiet', action='store_const',
                const=logging.ERROR, dest='loglevel',
                help="be completely quiet, log nothing")
        logging_grp.add_option('--warnings', action='store_const',
                const=logging.WARNING, dest='loglevel',
                help="log warnings in addition to errors")
        logging_grp.add_option('-v', '--verbose', action='store_const',
                const=logging.INFO, dest='loglevel',
                help="log ALL the things!")
        logging_grp.add_option('--debug', action='store_const',
                const=logging.DEBUG, dest='loglevel',
                help="log debugging info in addition to warnings and errors")
        logging_grp.add_option('--log', '-l', dest='logfile',
                help="log to the specified LOGFILE instead of standard out")
        parser.add_option_group(logging_grp)

        cli_options, args = parser.parse_args()

        # Set up logging
        # --------------
        logging_options = {
            'format': '%(levelname)s: %(message)s',
            'level': cli_options.loglevel,
        }
        if cli_options.logfile:
            logging_options['filename'] = cli_options.logfile
        else:
            logging_options['stream'] = sys.stdout

        logging.basicConfig(**logging_options)

        # Action!
        # -------
        self.generate_site()

        # Dev server
        # ----------
        if cli_options.runserver:
            ''' Run the dev server if the user said to, and watch the specified
            directories for changes. The server will regenerate the entire wok
            site if changes are found after every request.
            '''
            output_dir = os.path.join(self.options['output_dir'])
            host = '' if cli_options.address is None else cli_options.address
            port = 8000 if cli_options.port is None else cli_options.port
            server = dev_server(serv_dir=output_dir, host=host, port=port,
                dir_mon=True,
                watch_dirs=[
                    self.options['media_dir'],
                    self.options['template_dir'],
                    self.options['content_dir']
                ],
                change_handler=self.generate_site)
            server.run()

    def generate_site(self):
        ''' Generate the wok site '''
        orig_dir = os.getcwd()
        os.chdir(self.SITE_ROOT)

        self.all_pages = []

        self.read_options()
        self.sanity_check()
        self.load_hooks()

        self.run_hook('site.start')

        self.prepare_output()
        self.load_pages()
        self.make_tree()
        self.render_site()

        self.run_hook('site.done')

        os.chdir(orig_dir)

    def read_options(self):
        """Load options from the config file."""
        self.options = Engine.default_options.copy()

        if os.path.isfile('config'):
            with open('config') as f:
                yaml_config = yaml.load(f)

            if yaml_config:
                self.options.update(yaml_config)

        # Make authors a list, even only a single author was specified.
        authors = self.options.get('authors', self.options.get('author', None))
        if isinstance(authors, list):
            self.options['authors'] = [Author.parse(a) for a in authors]
        elif isinstance(authors, str):
            csv = authors.split(',')
            self.options['authors'] = [Author.parse(a) for a in csv]
            if len(self.options['authors']) > 1:
                logging.warn('Deprecation Warning: Use YAML lists instead of '
                        'CSV for multiple authors. i.e. ["John Doe", "Jane '
                        'Smith"] instead of "John Doe, Jane Smith". In config '
                        'file.')

        if '{type}' in self.options['url_pattern']:
            logging.warn('Deprecation Warning: You should use {ext} instead '
                    'of {type} in the url pattern specified in the config '
                    'file.')

    def sanity_check(self):
        """Basic sanity checks."""
        # Make sure that this is (probabably) a wok source directory.
        if not (os.path.isdir('templates') or os.path.isdir('content')):
            logging.critical("This doesn't look like a wok site. Aborting.")
            sys.exit(1)

    def load_hooks(self):
        try:
            sys.path.append('hooks')
            import __hooks__
            self.hooks = __hooks__.hooks
            logging.info('Loaded {0} hooks: {0}'.format(self.hooks))
        except ImportError as e:
            if "__hooks__" in str(e):
                logging.info('No hooks module found.')
            else:
                # don't catch import errors raised within a hook
                logging.info('Import error within hooks.')
                raise ImportError(e)

    def run_hook(self, hook_name, *args):
        """ Run specified hooks if they exist """
        logging.debug('Running hook {0}'.format(hook_name))
        returns = []
        try:
            for hook in self.hooks.get(hook_name, []):
                returns.append(hook(self.options, *args))
        except AttributeError:
            logging.info('Hook {0} not defined'.format(hook_name))
        return returns

    def prepare_output(self):
        """
        Prepare the output directory. Remove any contents there already, and
        then copy over the media files, if they exist.
        """
        if os.path.isdir(self.options['output_dir']):
            for name in os.listdir(self.options['output_dir']):
                # Don't remove dotfiles
                if name[0] == ".":
                    continue
                path = os.path.join(self.options['output_dir'], name)
                if os.path.isfile(path):
                    os.unlink(path)
                else:
                    shutil.rmtree(path)
        else:
            os.mkdir(self.options['output_dir'])

        self.run_hook('site.output.pre', self.options['output_dir'])

        # Copy the media directory to the output folder
        if os.path.isdir(self.options['media_dir']):
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
                logging.warning('There was a problem copying the media files '
                                'to the output directory.')

            self.run_hook('site.output.post', self.options['output_dir'])

    def load_pages(self):
        """Load all the content files."""
        # Load pages from hooks (pre)
        for pages in self.run_hook('site.content.gather.pre'):
            if pages:
                self.all_pages.extend(pages)

        # Load files
        for root, dirs, files in os.walk(self.options['content_dir']):
            # Grab all the parsable files
            for f in files:
                # Don't parse hidden files.
                if f.startswith('.'):
                    continue

                ext = f.split('.')[-1]
                renderer = renderers.Plain

                for r in renderers.all:
                    if ext in r.extensions:
                        renderer = r
                        break
                else:
                    logging.warning('No parser found '
                            'for {0}. Using default renderer.'.format(f))
                    renderer = renderers.Renderer

                p = Page.from_file(os.path.join(root, f), self.options, self, renderer)
                if p and p.meta['published']:
                    self.all_pages.append(p)

        # Load pages from hooks (post)
        for pages in self.run_hook('site.content.gather.post', self.all_pages):
            if pages:
                self.all_pages.extend(pages)

    def make_tree(self):
        """
        Make the category pseudo-tree.

        In this structure, each node is a page. Pages with sub pages are
        interior nodes, and leaf nodes have no sub pages. It is not truly a
        tree, because the root node doesn't exist.
        """
        self.categories = {}
        site_tree = []
        # We want to parse these in a approximately breadth first order
        self.all_pages.sort(key=lambda p: len(p.meta['category']))

        # For every page
        for p in self.all_pages:
            # If it has a category (ie: is not at top level)
            if len(p.meta['category']) > 0:
                top_cat = p.meta['category'][0]
                if not top_cat in self.categories:
                    self.categories[top_cat] = []

                self.categories[top_cat].append(p.meta)

            try:
                # Put this page's meta in the right place in site_tree.
                siblings = site_tree
                for cat in p.meta['category']:
                    # This line will fail if the page is an orphan
                    parent = [subpage for subpage in siblings
                                 if subpage['slug'] == cat][0]
                    siblings = parent['subpages']
                siblings.append(p.meta)
            except IndexError:
                logging.error('It looks like the page "{0}" is an orphan! '
                        'This will probably cause problems.'.format(p.path))

    def render_site(self):
        """Render every page and write the output files."""
        # Gather tags
        tag_set = set()
        for p in self.all_pages:
            tag_set = tag_set.union(p.meta['tags'])
        tag_dict = dict()
        for tag in tag_set:
            # Add all pages with the current tag to the tag dict
            tag_dict[tag] = [p.meta for p in self.all_pages
                                if tag in p.meta['tags']]

        # Gather slugs
        slug_dict = dict((p.meta['slug'], p.meta) for p in self.all_pages)

        for p in self.all_pages:
            # Construct this every time, to avoid sharing one instance
            # between page objects.
            templ_vars = {
                'site': {
                    'title': self.options.get('site_title', 'Untitled'),
                    'datetime': datetime.now(),
                    'date': datetime.now().date(),
                    'time': datetime.now().time(),
                    'tags': tag_dict,
                    'pages': self.all_pages[:],
                    'categories': self.categories,
                    'slugs': slug_dict,
                },
            }

            for k, v in self.options.iteritems():
                if k not in ('site_title', 'output_dir', 'content_dir',
                        'templates_dir', 'media_dir', 'url_pattern'):

                    templ_vars['site'][k] = v

            if 'author' in self.options:
                templ_vars['site']['author'] = self.options['author']

            # Rendering the page might give us back more pages to render.
            new_pages = p.render(templ_vars)

            if p.meta['make_file']:
                p.write()

            if new_pages:
                logging.debug('found new_pages')
                self.all_pages += new_pages

if __name__ == '__main__':
    Engine()
    exit(0)
