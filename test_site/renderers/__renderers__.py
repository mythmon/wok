import logging

try:
    from bs4 import BeautifulSoup
    def render(plain, page_meta):
        soup = BeautifulSoup(plain)
        return soup.body

except ImportError:
    import cgi
    logging.warning('HTML rendering relies on the BeautifulSoup library.')
    def render(plain, page_meta):
        return '<h1>Rendering error</h1>' \
            + '<p><code>BeautifulSoup</code> could not be loaded.</p>' \
            + '<p>Original plain document follows:</p>' \
            + '<p>' + cgi.escape(plain) + '</p>'


renderers = {
    'html': type('',(object,), { 'render': staticmethod(render) })
}
