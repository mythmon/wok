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

class dev_server:

    def __init__(self, serv_dir=None, host='', port=8000, watch_dirs=None, 
            change_handler=None):
        ''' Initialize a new development server on `host`:`port`, and serve the
        files in `serv_dir`. If `serv_dir` is not provided, it will use the 
        current working directory.
        '''
        self.serv_dir = serv_dir
        self.host = host
        self.port = port
        self.watch_dirs = watch_dirs
        self.change_handler = change_handler
        self.file_state = None

    def run(self):
        if self.serv_dir:
            os.chdir(self.serv_dir)

        server = HTTPServer
        req_handler = SimpleHTTPRequestHandler
        httpd = server((self.host, self.port), req_handler)
        socket_info = httpd.socket.getsockname()

        print "Starting dev server on http://%s:%s... (Ctrl-c to stop)"\
                %(socket_info[0], socket_info[1])
        try:
            while True:
                if self.watch_dirs:
                    self.file_state = self.take_snapshot()

                httpd.handle_request()

                if self.watch_dirs and self.take_snapshot() != self.file_state:
                    self.change_handler()
                    
        except KeyboardInterrupt:
            print "\nStopping development server..."

    def take_snapshot(self):
        modtime_sum = 0
        for d in self.watch_dirs:
            for root, dirs, files in os.walk(d):
                for f in files:
                    abspath = os.path.join(root, f)
                    modtime_sum += os.stat(abspath).st_mtime
        return modtime_sum
