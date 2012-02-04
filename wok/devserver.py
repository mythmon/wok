''' Really simple HTTP server for development.

Do *NOT* attempt to use this as anything resembling a production server. It is
meant to be used as a development test server only.

You might ask, "Why do I need a development server for static pages?" One
hyphenated modifier: "root-relative." Since wok dumps all of the media files
in the root output directory, pages that reside inside subdirectories still
need to access these media files in a unified way.

E.g., if you include `base.css` in your `base.html` template, `base.css` should
be accessable to any page that uses `base.html`, even if it's a categorized
page, and thus, goes into a subdirectory. This way, your CSS include tag could
read `<link type='text/css' href='/base.css' />` (note the '/' in the `href`
property) and `base.css` can be accessed from anywhere.
'''

import sys
import os
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

def run(address=None, port=None, serv_dir=None):
    ''' Run the development server on `address`:`port` and server the
    directory `serv_dir`. (If `serv_dir` is not provided, it will use
    the current working directory.)
    '''
    if not address:
        address = ''
    if not port:
        port = 8000
    else:
        port = int(port)
    if serv_dir:
        os.chdir(serv_dir)
    server_class = HTTPServer
    handler_class = SimpleHTTPRequestHandler
    httpd = server_class((address, port), handler_class)
    socketInfo = httpd.socket.getsockname()
    print "Development HTTP server running on http://%s:%s (Ctrl-c to stop)"\
            %(socketInfo[0], socketInfo[1])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "\nbye!"
        exit(0)
