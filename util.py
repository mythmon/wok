class out(object):
    def error(kind, message):
        print("Error from {}: {}".format(kind, message))

    def warn(kind, message):
        print("Warning from {}: {}".format(kind, message))

    def debug(kind, message):
        print("Debug from {}: {}".format(kind, message))

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

