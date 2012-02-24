# vim: set fileencoding=utf8 :
"""Some hooks that might be useful."""

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
            raise DependencyException('To use the HeadingAnchors hook, you must '
                                      'install the library lxml.')
        self.max_heading = max_heading
        logging.info('Loaded hook HeadingAnchors')

    def __call__(self, page):
        logging.debug('Called hook HeadingAnchors on {0}'.format(page))
        parser = etree.HTMLParser()
        sio_source = StringIO(page.rendered)
        tree = etree.parse(sio_source, parser)

        for lvl in range(1, self.max_heading+1):
            headings = tree.iterfind('//h{0}'.format(lvl))
            for heading in headings:
                if not heading.text:
                    continue
                logging.debug('[hook/HeadingAnchors] {0} {1}'.format(heading, heading.text))

                name = 'heading-{0}'.format(slugify(heading.text))
                anchor = etree.Element('a')
                anchor.set('class', 'heading_anchor')
                anchor.set('href', '#' + name)
                anchor.set('title', 'Permalink to this section.')
                anchor.text = u'¶'
                heading.append(anchor)

                heading.set('id', name)

        sio_destination = StringIO()
        tree.write(sio_destination)
        page.rendered = sio_destination.getvalue()
