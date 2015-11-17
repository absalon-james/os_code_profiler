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


class FakeThreadGroup(object):
    def __init__(self):
        self.thread_counter = 0

    def add_thread(self, *args, **kwargs):
        self.thread_counter += 1


class TestNovaServiceDumper(unittest.TestCase):
    """
    Tests the working thread function.

    """

    results_dir = os.path.join(os.path.dirname(__file__), 'data')

    def tearDown(self):
        """
        Remove a stats dump file if it exists.

        """
        for f in os.listdir(self.results_dir):
            if f.endswith('.stats'):
                os.remove(os.path.join(self.results_dir, f))

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
        dumper = _Dumper(object(), config, [])
        with self.assertRaises(NovaServiceProfilingException):
            dumper.work()

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    def test_set_started(self, mocked_start):
        """
        Tests that _started attribute is set at the beginning of work()

        """
        config = self.create_config()
        dumper = _Dumper(object(), config, [])
        dumper._stop = True
        dumper.work()
        self.assertTrue(dumper._started is not None)

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    def test_set_ended(self, mocked_start):
        """
        Tests that _ended attribute is set at the end of work()

        """
        config = self.create_config()
        dumper = _Dumper(object(), config, [])
        dumper._stop = True
        dumper.work()
        self.assertTrue(dumper._ended is not None)

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    @mock.patch('os_code_profiler.decorators.nova.profiler.stop')
    @mock.patch('os_code_profiler.decorators.nova.profiler.clear_stats')
    @mock.patch(
        'os_code_profiler.decorators.nova.utils.utc_seconds',
        return_value=1
    )
    def test_dump_with_clear(
        self, mocked_time, mocked_clear,
        mocked_stop, mocked_start
    ):
        """
        Tests that dump stops, clears, then restarts the profiler

        """
        config = self.create_config(clear_each_interval=True)
        dumper = _Dumper(object(), config, [])
        dumper._started = 1
        dumper._dump()
        mocked_stop.assert_called_with()
        mocked_clear.assert_called_with()
        mocked_start.assert_called_with()
        self.assertEquals(mocked_time.call_count, 3)

    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    @mock.patch('os_code_profiler.decorators.nova.profiler.stop')
    @mock.patch('os_code_profiler.decorators.nova.profiler.clear_stats')
    def test_dump_no_clear(self, mocked_clear, mocked_stop, mocked_start):
        """
        Tests that the profiler is not stopped, cleared, then restarted

        """
        config = self.create_config(clear_each_interval=False)
        dumper = _Dumper(object(), config, [])
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
        dumper = _Dumper(object(), config, [])
        dumper.set_clock_type()
        mocked.assert_called_with('blah')

    def test_outputs_init(self):
        """
        Tests that the list of outputs passed to init
        is saved to the dumper's outputs

        """
        config = self.create_config()
        outputs = ['a', 'b']
        dumper = _Dumper(object(), config, outputs)
        self.assertEquals(dumper._outputs, outputs)

    @mock.patch(
        'os_code_profiler.decorators.nova.profiler.get_func_stats',
        return_value=5
    )
    @mock.patch('os_code_profiler.decorators.nova.profiler.start')
    @mock.patch('os_code_profiler.decorators.nova.profiler.stop')
    @mock.patch('os_code_profiler.decorators.nova.profiler.clear_stats')
    def test_dump_outputs(self, *mocked):
        """
        Tests that the write method of each output is called
        during a dump.

        """
        class FakeOutput(object):
            def write(self, context, stats):
                pass

        config = self.create_config()
        outputs = [FakeOutput(), FakeOutput()]
        for o in outputs:
            o.write = mock.Mock()

        dumper = _Dumper(object(), config, outputs)
        dumper._dump()
        for o in outputs:
            self.assertEquals(o.write.call_count, 1)


class TestNovaService(unittest.TestCase):
    """
    Class for testing the nova service decorator.

    """
    def test_callable_instance(self):
        """
        Tests that Service is an instance of ServiceCallable

        """
        self.assertTrue(isinstance(Service, _ServiceDecorator))

    @mock.patch(
        'os_code_profiler.decorators.nova.ProfilingConfig',
        return_value=FakeConfig({})
    )
    def test_config(self, mocked_config_class):
        """
        Asserts that the profiling config class is used.

        """
        class FakeModule():
            class Service(object):
                def __init__(self, threads=1000):
                    self.tg = FakeThreadGroup()

        config_dict = {}
        module = FakeModule()
        module = Service(module, config_dict)
        module.Service()
        mocked_config_class.assert_called_with(config_dict)

    def test_thread_group_add_method(self):
        """
        Tests that the add_thread method of a service's threadgroup
        is called.

        """
        class FakeModule():
            class Service(object):
                def __init__(self, threads=1000):
                    self.tg = FakeThreadGroup()
        config_dict = {}
        module = FakeModule()
        module = Service(module, config_dict)
        s = module.Service()
        self.assertEquals(s.tg.thread_counter, 1)
