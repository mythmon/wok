import logging

from wok import util

# Check for pygments
try:
    import pygments
    have_pygments = True
except ImportError:
    logging.info('Pygments not enabled.')
    have_pygments = False

# List of available renderers
all = []

class Renderer(object):
    extensions = []

    @classmethod
    def render(cls, plain):
        return plain
all.append(Renderer)

class Plain(Renderer):
    """Plain text renderer. Replaces new lines with html </br>s"""
    extensions = ['txt']

    @classmethod
    def render(cls, plain):
        return plain.replace('\n', '<br>')
all.append(Plain)

# Include markdown, if it is available.
try:
    from markdown import markdown
    class Markdown(Renderer):
        """Markdown renderer."""
        extensions = ['markdown', 'mkd']

        plugins = ['def_list', 'footnotes']
        if have_pygments:
            plugins.append('codehilite(css_class=highlight)')

        @classmethod
        def render(cls, plain):
            return markdown(plain, Markdown.plugins)

    all.append(Markdown)

except ImportError:
    logging.info('Markdown not enabled.')

# Include ReStructuredText Parser, if we have docutils
try:

    import docutils.core
    from docutils.writers.html4css1 import Writer as rst_html_writer
    from docutils.parsers.rst import directives

    if have_pygments:
        from wok.rst_pygments import Pygments as RST_Pygments
        directives.register_directive('Pygments', RST_Pygments)

    class ReStructuredText(Renderer):
        """reStructuredText renderer."""
        extensions = ['rst']

        @classmethod
        def render(cls, plain):
            w = rst_html_writer()
            return docutils.core.publish_parts(plain, writer=w)['body']

    all.append(ReStructuredText)
except:
    logging.info('reStructuredText not enabled.')

if len(all) <= 2:
    print('You probably want to install either Markdown or docutils '
        '(reStructuredText). Otherwise only plain text input will be '
        'supported.')
