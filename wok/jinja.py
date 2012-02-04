import glob
import os

from jinja2.loaders import FileSystemLoader, TemplateNotFound
from jinja2.loaders import split_template_path

class AmbiguousTemplate(Exception):
    pass

class GlobFileLoader(FileSystemLoader):
    """
    As ``jinja2.loaders.FileSystemLoader`` except allow support for globbing.

    The loader takes the path to the templates as string, or if multiple
    locations are wanted a list of them which is then looked up in the
    given order:

    >>> loader = GlobFileLoader('/path/to/templates')
    >>> loader = GlobFileLoader(['/path/to/templates', '/other/path'])

    Per default the template encoding is ``'utf-8'`` which can be changed
    by setting the `encoding` parameter to something else.
    """

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            globbed_filename = os.path.join(searchpath, *pieces)
            filenames = glob.glob(globbed_filename)
            if len(filenames) > 1:
                raise AmbiguousTemplate(template)
            elif len(filenames) < 1:
                continue
            filename = filenames[0]

            with open(filename) as f:
                contents = f.read().decode(self.encoding)

            mtime = os.path.getmtime(filename)
            def uptodate():
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        else:
            raise TemplateNotFound(template)
