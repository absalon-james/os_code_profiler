import mock
import unittest

from os_code_profiler.common.profiling import Context


class TestContext(unittest.TestCase):
    """
    Tests the profiling context

    """
    @mock.patch(
        'os_code_profiler.common.profiling.socket.gethostname',
        return_value='mocked_hostname'
    )
    def test_hostname(self, mocked_gethostname):
        """
        If hostname is provided to context, context should use that one
        Otherwise hostname should be computed.

        """
        # Test provided
        ctx = Context(hostname='blah')
        self.assertEquals(ctx.hostname, 'blah')

        # Test not provided
        ctx = Context()
        self.assertEquals(ctx.hostname, 'mocked_hostname')

    @mock.patch('os_code_profiler.common.profiling.os.getpid', return_value=1)
    def test_pid(self, mocked_getpid):
        """
        If pid is provided, context should use that one
        Otherwise pid should be computed.

        """
        # Test provided
        ctx = Context(pid=5)
        self.assertEquals(ctx.pid, 5)

        # Test not provided
        ctx = Context()
        self.assertEquals(ctx.pid, 1)

    @mock.patch(
        'os_code_profiler.common.profiling.utils.utc_seconds',
        return_value=5
    )
    def test_started(self, mocked_time):
        """
        If started is provided, use that otherwise use now.

        """
        ctx = Context(started=10)
        self.assertEquals(ctx.started, 10)

        ctx = Context()
        self.assertEquals(ctx.started, 5)

    @mock.patch(
        'os_code_profiler.common.profiling.utils.utc_seconds',
        return_value=5
    )
    def test_ended(self, mocked_time):
        """
        If ended is provided, use that. Otherwise, use now

        """
        ctx = Context(ended=10)
        self.assertEquals(ctx.ended, 10)

        ctx = Context()
        self.assertEquals(ctx.ended, 5)

    def test_topic(self):
        """
        Tests the topic. A provided topic should be used. If not provided,
        use 'unknown_topic'

        """
        ctx = Context(topic="blah")
        self.assertEquals(ctx.topic, "blah")

        ctx = Context()
        self.assertEquals(ctx.topic, "unknown")
