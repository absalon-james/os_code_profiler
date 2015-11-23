import GreenletProfiler as profiler
import time

from eventlet import sleep

from os_code_profiler.common.decorators import Base as BaseDecorator
from os_code_profiler.common.profiling import \
    Config as ProfilingConfig,\
    Context as ProfilingContext
from os_code_profiler.common import utils


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
    def __init__(self, service, config, outputs):
        """
        @param service - Service object
        @param config - ProfilingConfig object
        @param outputs - List of output objects

        """
        self._config = config
        self._stop = False
        self._sub_interval = 1
        self._outputs = outputs

        self._started = None
        self._ended = None
        self._topic = getattr(service, 'topic', 'nova-unknown')

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
            self._ended = utils.utc_seconds()

        # Dump the stats
        stats = profiler.get_func_stats()
        ctx = ProfilingContext(
            started=self._started, ended=utils.utc_seconds(),
            topic=self._topic
        )
        for o in self._outputs:
            try:
                o.write(ctx, stats)
            except Exception:
                # @TODO - Possibly do something with logging
                pass

        # If clearing each interval, clear stats and restart profiler
        if self._config.clear_each_interval:
            profiler.clear_stats()
            profiler.start()
            self.started = utils.utc_seconds()

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
        self._started = utils.utc_seconds()

        last_dumped = time.time()

        while not self.should_stop():
            # Sleep for less than whole interval for faster interrupts
            sleep(self._sub_interval)
            checked = time.time()
            # Only take action if we have exceeded the interval period
            if (checked - last_dumped) > self._config.interval:
                self._dump()
                # Update last dumped
                last_dumped = checked

        # Finally stop the profiler
        profiler.stop()
        self._ended = utils.utc_seconds()


class _ServiceDecorator(BaseDecorator):
    """
    Callable that augments the nova service to spin up an additional
    green thread on the service's thread pool.

    """
    def __init__(self):
        super(_ServiceDecorator, self).__init__('__nova_service_decorator__')

    def _decorate(self, module, config):
        """
        Looks for the service class and alters the __init__ method
        to additionaly spawn a green thread on the threadgroup
        that will report code profiling statistics.

        @param module - Module to decorate
            (should be nova.openstack.common.service)
        @param config - Dictionary to configure the decoration.

        """
        klass = getattr(module, 'Service', None)
        if klass is None:
            return module

        old_init = getattr(klass, '__init__', None)
        if old_init is None:
            return module

        # Replace init method with new one
        def new_init(init_self, *args, **kwargs):
            """
            Replacement for __init__.
            Calls the original __init__ and then spawns a thread
            on the thread group.

            """
            # Call the old init method
            old_init(init_self, *args, **kwargs)

            # Create a profile config from config
            profile_config = ProfilingConfig(config)

            # Create output instances
            loader = utils.PluginLoader()
            outputs = []
            for p_name, p_config in config.get('outputs', {}).iteritems():
                outputs.append(loader.load(p_name, config=p_config))

            # Create the dumper
            dumper = _Dumper(init_self, profile_config, outputs)

            # Use the service's threadsgroup to add a thread
            init_self.tg.add_thread(dumper.work)

        setattr(klass, '__init__', new_init)
        return module

Service = _ServiceDecorator()
