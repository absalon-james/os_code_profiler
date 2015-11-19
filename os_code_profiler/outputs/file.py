import datetime
import os


class FileOutput(object):
    """
    Class for outputting profiling results to a file.

    """
    def __init__(self, config):
        """
        """
        self._results_dir = config.get('results_dir',
                                       '/var/log/os_code_profiler')

    def _path(self, ctx):
        """
        Returns the base path for the results file.

        @param ctx - Context object
        @returns - String

        """
        return os.path.join(self._results_dir, ctx.hostname, ctx.topic)

    def _mkdirs(self, path):
        """
        Creates hostname/topic subdirectories

        @param ctx - Context object

        """
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    def _filename(self, ctx):
        """
        Creates a file name from ctx

        @param ctx - Context object
        @returns - String

        """
        start = datetime.datetime.utcfromtimestamp(ctx.started)
        end = datetime.datetime.utcfromtimestamp(ctx.ended)
        return '%s_to_%s_%s.stats' % (start.isoformat(), end.isoformat(), ctx.pid)

    def write(self, ctx, stats):
        """
        Writes the stats object to a file using the stats' save method.

        @param ctx - Context object
        @param stats- yFuncStats object from yappi/GreenletProfiler

        """
        path = self._path(ctx)
        self._mkdirs(path)
        fullname = os.path.join(path, self._filename(ctx))
        stats.save(fullname)
