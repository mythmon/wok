try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase

from datetime import date, time, datetime, tzinfo

from wok import util

class TestDatetimes(TestCase):

    def setUp(self):
        """
        The date used is February 3rd, 2011 at 00:23 in the morning.

        The datetime is the first commit of wok.
        The date is the day this test was first written.
        The time is pi second.
        """
        self.datetime = datetime(2011, 2, 3, 0, 23, 0, 0)
        self.date = date(2011, 10, 12)
        self.time = time(3, 14, 15, 0)

    def test_blanks(self):
        inp = {}
        out = {
            'datetime': None,
            'date': None,
            'time': None,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_just_date(self):
        inp = {'date': self.date}
        out = {
            'datetime': datetime(2011, 10, 12, 0, 0, 0, 0),
            'date': self.date,
            'time': None,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_just_time(self):
        t = self.time # otherwise the datetime line gets awful
        inp = {'time': t}
        out = {
            'datetime': None,
            'date': None,
            'time': t,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_date_and_times(self):
        inp = {'date': self.date, 'time': self.time}
        out = {
            'datetime': datetime(2011, 10, 12, 3, 14, 15, 0),
            'date': self.date,
            'time': self.time,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_just_datetime(self):
        inp = {'datetime': self.datetime}
        out = {
            'datetime': self.datetime,
            'date': self.datetime.date(),
            'time': self.datetime.time(),
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_datetime_and_date(self):
        inp = {'datetime': self.datetime, 'date': self.date}
        out = {
           'datetime': datetime(2011, 10, 12, 0, 23, 0, 0),
           'date': self.date,
           'time': self.datetime.time(),
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_datetime_and_time(self):
        inp = {'datetime': self.datetime, 'time': self.time}
        out = {
            'datetime': datetime(2011, 2, 3, 3, 14, 15, 0),
            'date': self.datetime.date(),
            'time': self.time,
         }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_all(self):
        inp = {'datetime': self.datetime, 'date': self.date, 'time': self.time}
        out = {
            'datetime': datetime(2011, 10, 12, 3, 14, 15, 0),
            'date': self.date,
            'time': self.time,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

    def test_types(self):
        """
        YAML doesn't always give us the types we want. Handle that correctly.
        """
        # Yaml will only make something a datetime if it also includes a time.
        inp = {'datetime': date(2011, 12, 25)}
        out = {
            'datetime': datetime(2011, 12, 25),
            'date': date(2011, 12, 25),
            'time': None,
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)

        # Yaml likes to give times as the number of seconds.
        inp = {'date': self.date, 'time': 43200}
        out = {
            'datetime': datetime(2011, 10, 12, 12, 0, 0),
            'date': self.date,
            'time': time(12, 0, 0),
        }

        util.date_and_times(inp)
        self.assertEquals(inp, out)
