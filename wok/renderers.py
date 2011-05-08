from markdown import markdown
import docutils.core
from docutils.writers.html4css1 import Writer as rst_html_writer

class Renderer(object):
    extensions = []

    @classmethod
    def render(cls, plain):
        return plain

class Markdown(Renderer):
    extensions = ['markdown', 'mkd']

    @classmethod
    def render(cls, plain):
        return markdown(plain, ['def_list', 'footnotes'])

class ReStructuredText(Renderer):
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
