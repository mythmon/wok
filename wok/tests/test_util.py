try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase

from wok import util

class TestSlugs(TestCase):

    def test_noop(self):
        """Tests that is good slug gets passed through unmodified."""
        orig = u'agoodslug'
        slug = orig
        self.assertEqual(slug, util.slugify(orig))

    def test_caps(self):
        """Check that case get converted right."""
        orig = u'abcdABCD'
        slug = orig.lower()
        self.assertEqual(slug, util.slugify(orig))

    def test_spaces(self):
        """Check that spaces are converted to the seperator character."""
        orig = u'hello world'
        slug = u'hello-world'
        self.assertEqual(slug, util.slugify(orig))

    def test_punctuation(self):
        """Check that punctuation is handled right."""
        orig = u"This has... punctuation! *<yo>*."
        slug = u'this-has-punctuation-yo'
        self.assertEqual(slug, util.slugify(orig))

    def test_unicode(self):
        """Check that unicode is properly converted."""
        pass

    def test_apostrophes(self):
        """Check that apostrophes in words don't end up as ugly seperators"""
        orig = u"Don't use Bob's stuff"
        slug = u'dont-use-bobs-stuff'
        self.assertEqual(slug, util.slugify(orig))

    test_apostrophes.todo = "Apostrophes are treated like normal words right now"
