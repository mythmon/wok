from markdown import markdown

class Renderer(object):
    extensions = []

    @classmethod
    def render(cls, plain):
        return plain

Plain = Renderer

class Markdown(Renderer):
    extensions = ['markdown', 'mkd']

    @classmethod
    def render(cls, plain):
        return markdown(plain, ['def_list', 'footnotes'])

all = [Plain, Markdown]
