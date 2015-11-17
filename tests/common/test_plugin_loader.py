import os
import sys
import unittest

from os_code_profiler.common.utils import PluginLoader


class TestPluginLoader(unittest.TestCase):
    """
    Tests for the Plugin Loader

    """

    test_module_path = os.path.join(os.path.dirname(__file__),
                                    'packages')

    def setUp(self):
        """
        Add fake package path to path

        """
        sys.path.append(self.test_module_path)

    def tearDown(self):
        """
        Remove fake package path from path

        """
        if self.test_module_path in sys.path:
            sys.path.remove(self.test_module_path)

    def test_import_error(self):
        """
        Tests that import error is raised for module that doesnt exist

        """
        config = {}
        class_name = 'blah.wrong.doesntexist'
        loader = PluginLoader()
        with self.assertRaises(ImportError):
            loader.load(class_name, config)

    def test_load(self):
        """
        Tests that an instance of a class is returned from
        the loader with a configuration passed to the init
        method.

        """
        config = {'a': 1, 'b': 2}
        class_name = 'fake_package.fake_module.FakePlugin'
        loader = PluginLoader()
        obj = loader.load(class_name, config)
        for key, value in config.iteritems():
            self.assertEquals(value, getattr(obj, key))
