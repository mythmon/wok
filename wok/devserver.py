''' Really simple HTTP *development* server

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

def run(serv_dir=None, host='', port=8000):
    ''' Run the development server on `host`:`port`, and serve the files in
    `serv_dir`. If `serv_dir` is not provided, it will use the current working 
    directory.
    '''

    if serv_dir:
        os.chdir(serv_dir)

    server = HTTPServer
    handler = SimpleHTTPRequestHandler
    httpd = server((host, port), handler)
    socket_info = httpd.socket.getsockname()

    print "Starting dev server on http://%s:%s... (Ctrl-c to stop)"\
            %(socket_info[0], socket_info[1])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "\nStopping development server..."

