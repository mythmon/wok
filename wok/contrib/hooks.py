# vim: set fileencoding=utf8 :
"""Some hooks that might be useful."""

import os
import subprocess
from StringIO import StringIO
import logging

from wok.exceptions import DependencyException
from wok.util import slugify

try:
    from lxml import etree
except ImportError:
    etree = None


class HeadingAnchors(object):
    """
    Put some paragraph heading anchors.

    Serves as a 'page.template.post' wok hook.
    """

    def __init__(self, max_heading=3):
        if not etree:
            logging.warning('To use the HeadingAnchors hook, you must install '
                'the library lxml.')
            return
        self.max_heading = max_heading
        logging.info('Loaded hook HeadingAnchors')

    def __call__(self, page):
        if not etree:
            return
        logging.debug('Called hook HeadingAnchors on {0}'.format(page))
        parser = etree.HTMLParser()
        sio_source = StringIO(page.rendered)
        tree = etree.parse(sio_source, parser)

        for lvl in range(1, self.max_heading+1):
            headings = tree.iterfind('//h{0}'.format(lvl))
            for heading in headings:
                if not heading.text:
                    continue
                logging.debug('[HeadingAnchors] {0} {1}'
                        .format(heading, heading.text))

                name = 'heading-{0}'.format(slugify(heading.text))
                anchor = etree.Element('a')
                anchor.set('class', 'heading_anchor')
                anchor.set('href', '#' + name)
                anchor.set('title', 'Permalink to this section.')
                anchor.text = u'¶'
                heading.append(anchor)

                heading.set('id', name)

        sio_destination = StringIO()

	# Use the extension of the template to determine the type of document 
	if page.template.filename.endswith(".html") or page.filename.endswith(".htm"):
        	logging.debug('[HeadingAnchors] outputting {0} as HTML'.format(page))
	        tree.write(sio_destination, method='html')
	else:
        	logging.debug('[HeadingAnchors] outputting {0} as XML'.format(page))
	        tree.write(sio_destination)
        page.rendered = sio_destination.getvalue()


def compile_sass(output_dir):
    '''
    Compile Sass files -> CSS in the output directory.

    Any .scss or .sass files found in the output directory will be compiled
    to CSS using Sass. The compiled version of the file will be created in the
    same directory as the Sass file with the same name and an extension of
    .css. For example, foo.scss -> foo.css.

    Serves as a 'site.output.post' wok hook, e.g., your __hooks__.py file might
    look like this:

        from wok.contrib.hooks import compile_sass

        hooks = {
            'site.output.post':[compile_sass]
        }

    Dependencies:

        - Ruby
        - Sass (http://sass-lang.com)
    '''
    logging.info('Running hook compile_sass on {0}.'.format(output_dir))
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            fname, fext = os.path.splitext(f)
            if fext == ".scss" or fext == ".sass":
                abspath = os.path.abspath(root)
                sass_src = "%s/%s"%(abspath, f)
                sass_dest = "%s/%s.css"%(abspath, fname)
                sass_arg = "%s:%s"%(sass_src, sass_dest)
                logging.debug('[hook/sass] sass {0}'.format(sass_arg))
                try:
                    subprocess.call(['sass', sass_arg])
                except OSError:
                    logging.warning('[hook/compile_sass] Could not run SASS ' +
                                    'hook. (Is SASS installed?)')
