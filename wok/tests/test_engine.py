import os
import shutil
import sys
import tempfile

try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase

from wok import renderers
from wok.engine import Engine


DefaultRenderers = {}

def setUpModule():
    for renderer in renderers.all:
        DefaultRenderers.update((ext, renderer) for ext in renderer.extensions)


class TestEngine(TestCase):

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()
        os.chdir(self.tmp_path)

    def tearDown(self):
        os.chdir('..')
        if self.tmp_path is not None:
            shutil.rmtree(self.tmp_path)
            self.tmp_path = None
        if '__hooks__' in sys.modules:
            del sys.modules['__hooks__']
        if '__renderers__' in sys.modules:
            del sys.modules['__renderers__']

    def test_load_hooks_no_hooks(self):
        e = Engine.__new__(Engine)
        e.load_hooks()

        self.assertFalse(hasattr(e, 'hooks'))

    def test_load_hooks_empty_directory(self):
        os.mkdir('hooks')

        e = Engine.__new__(Engine)
        e.load_hooks()

        self.assertFalse(hasattr(e, 'hooks'))

    def test_load_hooks(self):
        os.mkdir('hooks')
        with open(os.path.join('hooks', '__hooks__.py'), 'a') as f:
            f.write('hooks = { "name": "action" }\n')

        e = Engine.__new__(Engine)
        e.load_hooks()

        self.assertIsInstance(e.hooks, dict)
        self.assertIn('name', e.hooks)
        self.assertEqual(e.hooks['name'], 'action')

    def test_load_renderers_no_ext_renderers(self):
        e = Engine.__new__(Engine)
        e.load_renderers()

        self.assertIsInstance(e.renderers, dict)
        self.assertDictEqual(e.renderers, DefaultRenderers)

    def test_load_renderers_empty_directory(self):
        os.mkdir('renderers')

        e = Engine.__new__(Engine)
        e.load_renderers()

        self.assertIsInstance(e.renderers, dict)
        self.assertDictEqual(e.renderers, DefaultRenderers)

    def test_load_renderers(self):
        os.mkdir('renderers')
        with open(os.path.join('renderers', '__renderers__.py'), 'a') as f:
            f.write('renderers = { "html": "class" }\n')

        e = Engine.__new__(Engine)
        e.load_renderers()

        self.assertIsInstance(e.renderers, dict)
        self.assertDictContainsSubset(DefaultRenderers, e.renderers)
        self.assertIn('html', e.renderers)
        self.assertEqual(e.renderers['html'], 'class')
