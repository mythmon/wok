title: reStructuredText Test Page
slug: rst
category: tests
tags: [rest, sample]
---
This is the reStructuredText test page
======================================
This page tests

* That reStructuredText rendering works.
* That I know how to make a RST document.
* Python code highlighting works.

.. sourcecode:: python

    class Author(object):
        """Smartly manages a author with name and email"""
        parse_author_regex = re.compile(r'([^<>]*)( +<(.*@.*)>)$')

        def __init__(self, raw='', name=None, email=None):
            self.raw = raw
            self.name = name
            self.email = email

        @classmethod
        def parse(cls, raw):
            a = cls(raw)
            a.name, _, a.email = cls.parse_author_regex.match(raw).groups()

        def __str__(self):
            if not self.name:
                return self.raw
            if not self.email:
                return self.name

            return "{0} <{1}>".format(self.name, self.email)
