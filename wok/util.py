import os
import sys
import textwrap
import re
from unicodedata import normalize

class Out(object):

    def __init__(self):
        self.level = 1
        self.wrap = os.isatty(sys.stdout.fileno())

    def error(self, kind, message):
        if self.level >= 0:
            self.wrapped_print("Error from {0}: {1}".format(kind, message))

    def warn(self, kind, message):
        if self.level >= 1:
            self.wrapped_print("Warning from {0}: {1}".format(kind, message))

    def info(self, kind, message):
        if self.level >= 2:
            self.wrapped_print("Info from {0}: {1}".format(kind, message))

    def debug(self, kind, message):
        if self.level >= 3:
            self.wrapped_print("Debug from {0}: {1}".format(kind, message))

    def wrapped_print(self, message):
        if self.wrap:
            _,w = [int(n) for n in os.popen('stty size', 'r').read().split()]
            message = textwrap.fill(message, w)
        print(message)

out = Out()

# From http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    """
    Generates a slug that will only use ASCII, be all lowercase, have no
    spaces, and otherwise be nice for filenames, identifiers, and urls.
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

