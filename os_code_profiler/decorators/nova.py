import GreenletProfiler

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

    def set_clock_type(self):
        """
        Sets the clock type according to config

        """
        GreenletProfiler.set_clock_type(self._config.clock_type)

    def work(self):
        """
        Long running loop that periodically dumps the stats.

        """
        if GreenletProfiler.is_running():
            raise NovaServiceProfilingException("Profiling already enabled.")


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
