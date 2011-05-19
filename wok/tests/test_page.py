try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase

from wok.page import Page

class TestAuthor(TestCase):

    def test_author(self):
        a = Page.Author.parse('Bob Smith')
        self.assertEqual(a.raw, 'Bob Smith')
        self.assertEqual(a.name, 'Bob Smith')

        a = Page.Author.parse('Bob Smith <bob@here.com>')
        self.assertEqual(a.raw, 'Bob Smith <bob@here.com>')
        self.assertEqual(a.name, 'Bob Smith')
        self.assertEqual(a.email, 'bob@here.com')

        a = Page.Author.parse('<bob@here.com>')
        self.assertEqual(a.raw, '<bob@here.com>')
        self.assertEqual(a.email, 'bob@here.com')
