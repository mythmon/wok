import re
from unicodedata import normalize
from datetime import date, time, datetime, timedelta

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
