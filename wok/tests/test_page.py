try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase

from wok.page import Author

class TestAuthor(TestCase):

    def test_author(self):
        a = Author.parse('Bob Smith')
        self.assertEqual(a.raw, 'Bob Smith')
        self.assertEqual(a.name, 'Bob Smith')

        a = Author.parse('Bob Smith <bob@here.com>')
        self.assertEqual(a.raw, 'Bob Smith <bob@here.com>')
        self.assertEqual(a.name, 'Bob Smith')
        self.assertEqual(a.email, 'bob@here.com')

        a = Author.parse('<bob@here.com>')
        self.assertEqual(a.raw, '<bob@here.com>')
        self.assertEqual(a.email, 'bob@here.com')
