from markdown import markdown
import docutils.core

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
        return docutils.core.publish_parts(plain)['body']

Plain = Renderer

all = [Plain, Markdown]
