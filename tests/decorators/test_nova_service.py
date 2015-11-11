import mock
import os
import unittest

from os_code_profiler.decorators.nova import \
    NovaServiceProfilingException, \
    Service, \
    _ServiceDecorator, \
    _Dumper


def fake_start(builtins=False, profile_threads=True):
    raise(Exception('This should not be called'))


class FakeConfig():
    def __init__(self, d):
        self.__dict__ = d


class FakeModule():
    pass


class TestNovaServiceDumper(unittest.TestCase):
    """
    Tests the working thread function.

    """

    results_dir = os.path.basename(__file__)

    def create_config(self, clock_type='wall', interval=30,
                      clear_each_interval=True, results_dir=None):
        """
        Creates a fake configuration for all _Dumper instances

        """
        if results_dir is None:
            results_dir = self.results_dir

        return FakeConfig({
            'clock_type': clock_type,
            'interval': interval,
            'clear_each_interval': clear_each_interval,
            'results_dir': results_dir
        })

    @mock.patch(
        'os_code_profiler.decorators.nova.profiler.is_running',
        return_value=True
    )
    def test_profiling_already_enabled(self, mocked):
        """
        Worker method should raise exception if profiling already enabled.

        """
        config = self.create_config()
        dumper = _Dumper(config)
        with self.assertRaises(NovaServiceProfilingException):
            dumper.work()

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    @mock.patch('os_code_profiler.decorators.nova.profiler.stop')
    @mock.patch('os_code_profiler.decorators.nova.profiler.clear_stats')
    def test_dump_with_clear(self, mocked_clear, mocked_stop, mocked_start):
        """
        Tests that dump stops, clears, then restarts the profiler

        """
        config = self.create_config(clear_each_interval=True)
        dumper = _Dumper(config)
        dumper._dump()
        mocked_stop.assert_called_with()
        mocked_clear.assert_called_with()
        mocked_start.assert_called_with()

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    @mock.patch('os_code_profiler.decorators.nova.profiler.stop')
    @mock.patch('os_code_profiler.decorators.nova.profiler.clear_stats')
    def test_dump_no_clear(self, mocked_clear, mocked_stop, mocked_start):
        """
        Tests that the profiler is not stopped, cleared, then restarted

        """
        config = self.create_config(clear_each_interval=False)
        dumper = _Dumper(config)
        dumper._dump()
        mocked_stop.assert_not_called()
        mocked_clear.assert_not_called()
        mocked_start.assert_not_called()

    @mock.patch('os_code_profiler.decorators.nova.profiler.set_clock_type')
    def test_set_clock_type(self, mocked):
        """
        Tests setting of the clock type.

        """
        config = self.create_config()
        config.clock_type = 'blah'
        dumper = _Dumper(config)
        dumper.set_clock_type()
        mocked.assert_called_with('blah')

    def test_file_name(self):
        """
        Tests the name file name creation method of the dumper

        """
        pass


class TestNovaService(unittest.TestCase):
    """
    Class for testing the nova service decorator.

    """
    def test_callable_instance(self):
        """
        Tests that Service is an instance of ServiceCallable

        """
        self.assertTrue(isinstance(Service, _ServiceDecorator))


    @mock.patch('os_code_profiler.decorators.nova.ProfilingConfig',
                return_value=FakeConfig({}))
    def test_config(self, mocked_config_class):
        """
        Asserts that the profiling config class is used.
        """
        config_dict = {}
        module = FakeModule()
        Service(module, config_dict)
        mocked_config_class.assert_called_with(config_dict)
