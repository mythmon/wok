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

    def __init__(self, serv_dir=None, host='', port=8000, dir_mon=False,
            watch_dirs=[], change_handler=None):
        '''
        Initialize a new development server on `host`:`port`, and serve the
        files in `serv_dir`. If `serv_dir` is not provided, it will use the
        current working directory.

        If `dir_mon` is set, the server will check for changes before handling
        every request. If a change is detected, then wok will regenerate the
        site.
        '''
        self.serv_dir = os.path.abspath(serv_dir)
        self.host = host
        self.port = port
        self.dir_mon = dir_mon
        self.watch_dirs = [os.path.abspath(d) for d in watch_dirs]
        self.change_handler = change_handler

    def run(self):
        if self.serv_dir:
            os.chdir(self.serv_dir)

        if self.dir_mon:
            wrap = RebuildHandlerWrapper(self.change_handler, self.watch_dirs)
            req_handler = wrap.request_handler
        else:
            req_handler = SimpleHTTPRequestHandler

        httpd = HTTPServer((self.host, self.port), req_handler)
        socket_info = httpd.socket.getsockname()

        print("Starting dev server on http://%s:%s... (Ctrl-c to stop)"
                %(socket_info[0], socket_info[1]))
        print "Serving files from", self.serv_dir

        if self.dir_mon:
            print "Monitoring the following directories for changes: "
            for d in self.watch_dirs:
                print "\t", d
        else:
            print "Directory monitoring is OFF"

        httpd.serve_forever()


class RebuildHandlerWrapper(object):

    def __init__(wrap_self, rebuild, watch_dirs):
        """
        We can't pass arugments to HTTPRequestHandlers, because HTTPServer
        calls __init__. So make a closure.
        """
        wrap_self.rebuild = rebuild
        wrap_self.watch_dirs = watch_dirs
        wrap_self.modtime_sum = None
        wrap_self.changed = False
        wrap_self.take_snapshot()

        class RebuildHandler(SimpleHTTPRequestHandler):
            """Rebuild if something has changed."""

            def handle(self):
                "Handle a request and, if anything has changed, rebuild the site."
                wrap_self.take_snapshot()
                if wrap_self.changed:
                    wrap_self.rebuild()

                SimpleHTTPRequestHandler.handle(self)

        wrap_self.request_handler = RebuildHandler

    def take_snapshot(self):
        '''
        Take a 'snapshot' of the watched directories by returning a simple
        sum of the residing files' modification times.
        '''
        last_modtime_sum = self.modtime_sum
        self.modtime_sum = 0
        for d in self.watch_dirs:
            for root, dirs, files in os.walk(d):
                for f in files:
                    abspath = os.path.join(root, f)
                    self.modtime_sum += os.stat(abspath).st_mtime

        if last_modtime_sum is not None:
            self.changed = (last_modtime_sum != self.modtime_sum)
