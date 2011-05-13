# Markdown
from markdown import markdown
# reStructuredText
import docutils.core
from docutils.writers.html4css1 import Writer as rst_html_writer
from docutils.parsers.rst import directives
from wok.rst_pygments import Pygments as RST_Pygments

class Renderer(object):
    extensions = []

    @classmethod
    def render(cls, plain):
        return plain

class Markdown(Renderer):
    extensions = ['markdown', 'mkd']

    @classmethod
    def render(cls, plain):
        return markdown(plain, ['def_list', 'footnotes', 'codehilite(css_class=highlight )'])

class ReStructuredText(Renderer):
    directives.register_directive('Pygments', RST_Pygments)

    extensions = ['rst']

    @classmethod
    def render(cls, plain):
        w = rst_html_writer()
        return docutils.core.publish_parts(plain, writer=w)['body']

class Plain(Renderer):
    extensions = 'txt'

    @classmethod
    def render(cls, plain):
        return plain.replace('\n', '<br>')

all = [Renderer, Plain, Markdown, ReStructuredText]
