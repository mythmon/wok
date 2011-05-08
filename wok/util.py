import re
from unicodedata import normalize

class out(object):

    level = 2

    @classmethod
    def error(cls, kind, message):
        if cls.level >= 0:
            print("Error from {0}: {1}".format(kind, message))

    @classmethod
    def warn(cls, kind, message):
        if cls.level >= 1:
            print("Warning from {0}: {1}".format(kind, message))

    @classmethod
    def info(cls, kind, message):
        if cls.level >= 2:
            print("Info from {0}: {1}".format(kind, message))

    @classmethod
    def debug(cls, kind, message):
        if cls.level >= 3:
            print("Debug from {0}: {1}".format(kind, message))

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

