import re
from unicodedata import normalize
from datetime import date, time, datetime, timedelta

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

    result = delim.join(result)
    if result[0] == '-':
        result = result[1:]
    if result[-1] == '-':
        result = result[:-1]

    return unicode(result)


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
            if isinstance(meta['datetime'], datetime):
                date_part = meta['datetime'].date()
            elif isinstance(meta['datetime'], date):
                date_part = meta['datetime']

        if time_part is None and isinstance(meta['datetime'], datetime):
            time_part = meta['datetime'].time()

    if isinstance(time_part, int):
        seconds = time_part % 60
        minutes = (time_part / 60) % 60
        hours = (time_part / 3600)

        time_part = time(hours, minutes, seconds)

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

    if meta['date'] is None:
        meta['date'] = date(1970, 1, 1)
    if meta['time'] is None:
        meta['time'] = time()
    if meta['datetime'] is None:
        meta['datetime'] = datetime(1970, 1, 1)
