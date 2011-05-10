import re
from unicodedata import normalize

class Out(object):

    def __init__(self):
        self.level = 1

    def error(self, kind, message):
        if self.level >= 0:
            print("Error from {0}: {1}".format(kind, message))

    def warn(self, kind, message):
        if self.level >= 1:
            print("Warning from {0}: {1}".format(kind, message))

    def info(self, kind, message):
        if self.level >= 2:
            print("Info from {0}: {1}".format(kind, message))

    def debug(self, kind, message):
        if self.level >= 3:
            print("Debug from {0}: {1}".format(kind, message))

out = Out()

# From http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    """Generates a ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

