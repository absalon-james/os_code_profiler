import GreenletProfiler as profiler
import time

from os_code_profiler.common.decorators import Base as BaseDecorator
from os_code_profiler.common.profiling import Config as ProfilingConfig

class NovaServiceProfilingException(Exception):
    """
    Simple exception.

    """
    pass


class _Dumper():
    """
    Class for periodically dumping profiling stats for long running
    nova services.

    Includes a worker method that is intended to be run by spawning
    from a nova service threadgroup.

    """
    def __init__(self, config):
        """
        @param config - ProfilingConfig object

        """
        self._config = config
        self._stop = False
        self._sub_interval = 1

    def should_stop(self):
        """
        Returns whether or not profiler should stop
        """
        return self._stop

    def set_clock_type(self):
        """
        Sets the clock type according to config

        """
        profiler.set_clock_type(self._config.clock_type)

    def _dump(self):
        """
        Dumps the profiling stats.
        Also manages clearing stats if clearing each interval.

        """
        # If clearing each interval, stop profiler
        if self._config.clear_each_interval:
            profiler.stop()

        # Dump the stats
        #@TODO - Actual dump

        # If clearing each interval, clear stats and restart profiler
        if self._config.clear_each_interval:
            profiler.clear_stats()
            profiler.start()

    def work(self):
        """
        Long running loop that periodically dumps the stats.

        """
        if profiler.is_running():
            raise NovaServiceProfilingException("Profiling already enabled.")

        # Set clock type
        self.set_clock_type()

        # Start profiler
        profiler.start()

        last_dumped = time.time()

        while not self.should_stop():
            # Sleep for less than whole interval for faster interrupts
            eventlet.sleep(self._sub_interval)
            checked = time.time()
            # Only take action if we have exceeded the interval period
            if (checked - last_dumped) > self._config.interval:
                # Update last dumped
                last_dumped = checked

        # Finally stop the profiler
        profiler.stop()


class _ServiceDecorator(BaseDecorator):
    """
    Callable that augments the nova service to spin up an additional
    green thread on the service's thread pool.

    """
    def __init__(self):
        super(_ServiceDecorator, self).__init__('__nova_service_decorator__')

    def _decorate(self, module, config):
        config_obj = ProfilingConfig(config)
        return module

Service = _ServiceDecorator()
