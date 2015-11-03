import unittest

from os_code_profiler.common.profiling import \
    Config as ProfilingConfig, \
    ConfigException as ProfilingConfigException


class TestProfilingConfig(unittest.TestCase):
    """
    Tests configuration object for profiling.

    """
    def test_defaults(self):
        """
        Tests the default values where no config is present.

        """
        config_dict = {}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.clock_type, 'wall')
        self.assertEquals(config_obj.interval, 60 * 5)
        self.assertEquals(config_obj.clear_each_interval, True)
        self.assertEquals(config_obj.results_dir, '/tmp')

    def test_clock_type(self):
        """
        Tests clock type

        """
        # Lower
        config_dict = {"clock_type": 'cpu'}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.clock_type, 'cpu')

        # Upper
        config_dict = {"clock_type": 'CPU'}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.clock_type, 'cpu')

        # Invalid must be one of 'cpu' or 'wall'
        config_dict = {"clock_type": "invalid"}
        with self.assertRaises(ProfilingConfigException):
            config_obj = ProfilingConfig(config_dict)

    def test_interval(self):
        """
        Tests interval

        """
        config_dict = {"interval": 5}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.interval, 5)

        config_dict = {"interval": "5"}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.interval, 5)

        config_dict = {"interval": "kafive"}
        with self.assertRaises(Exception):
            config_obj = ProfilingConfig(config_dict)

    def test_clear_each_interval(self):
        """
        Tests the clear_each_interval

        """
        config_dict = {"clear_each_interval": False}
        config_obj = ProfilingConfig(config_dict)
        self.assertTrue(config_obj.clear_each_interval is False)

        config_dict = {"clear_each_interval": ""}
        config_obj = ProfilingConfig(config_dict)
        self.assertTrue(config_obj.clear_each_interval is False)

        config_dict = {"clear_each_interval": 0}
        config_obj = ProfilingConfig(config_dict)
        self.assertTrue(config_obj.clear_each_interval is False)

    def test_results_dir(self):
        """
        Tests the results dir

        """
        config_dict = {"results_dir": "/blah"}
        config_obj = ProfilingConfig(config_dict)
        self.assertEquals(config_obj.results_dir, "/blah")
