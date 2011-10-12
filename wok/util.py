import re
from unicodedata import normalize
from datetime import date, time, datetime

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


def chunk(li, n):
    """Yield succesive n-size chunks from l."""
    for i in xrange(0, len(li), n):
        yield li[i:i+n]

def date_and_times(meta):

    date_part = None
    time_part = None

    if 'date' in meta:
        date_part = meta['date']
    if 'time' in meta:
        time_part = meta['time']
    if 'datetime' in meta:
        if date_part is None:
            date_part = meta['datetime'].date()
        if time_part is None:
            time_part = meta['datetime'].time()

    meta['date'] = date_part
    meta['time'] = time_part

    if date_part is not None and time_part is not None:
        meta['datetime'] = datetime(date_part.year, date_part.month,
                date_part.day, time_part.hour, time_part.minute,
                time_part.second, time_part.microsecond, time_part.tzinfo)
    elif date_part is not None:
        meta['datetime'] = datetime(date_part.year, date_part.month, date_part.day)
    else:
        meta['datetime'] = None
