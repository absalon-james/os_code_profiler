import mock
import unittest

from os_code_profiler.outputs.file import FileOutput


class FakeContext(object):
    """Fake Context Class"""
    def __init__(self, hostname, pid, started, ended, topic):
        self.hostname = hostname
        self.pid = pid
        self.started = started
        self.ended = ended
        self.topic = topic


def error_makedirs(path):
    raise OSError((1, 'FakeError'))


class TestFileOutput(unittest.TestCase):
    """Tests the fileoutput"""

    hostname = 'ahost'
    pid = 999999
    topic = 'testing'
    started = 0
    started_string = '1970-01-01T00:00:00'
    ended = 1447866463.491419
    ended_string = '2015-11-18T17:07:43.491419'

    def create_ctx(self):
        """Creates simple context"""
        return FakeContext(self.hostname, self.pid,
                           self.started, self.ended, self.topic)

    def test_result_dir(self):
        """
        Init method should pull output directory

        Results dir should default to /var/log/os_code_profiler

        """
        # Test default
        config = {}
        o = FileOutput(config)
        self.assertEquals(o._results_dir, '/var/log/os_code_profiler')

        # Test provided
        config = {'results_dir': '/blah'}
        o = FileOutput(config)
        self.assertEquals(o._results_dir, '/blah')

    def test_path(self):
        """
        Result path should be results_dir/hostname/topic

        """
        config = {'results_dir': '/blah'}
        ctx = self.create_ctx()
        o = FileOutput(config)
        path = o._path(ctx)
        self.assertEquals(path, '/blah/%s/%s' % (self.hostname, self.topic))

    @mock.patch('os_code_profiler.outputs.file.os.makedirs')
    def test_mkdirs(self, mocked):
        """
        When writing the results, subdirectories of hostname
        and topic should be created

        """
        config = {}
        path = '/path/%s/%s' % (self.hostname, self.topic)
        o = FileOutput(config)
        o._mkdirs(path)
        mocked.assert_called_with(path)

    @mock.patch(
        'os_code_profiler.outputs.file.os.makedirs',
        side_effect=error_makedirs
    )
    @mock.patch(
        'os_code_profiler.outputs.file.os.path.isdir',
        return_value=True
    )
    def test_mkdirs_already_exists(self, mocked_isdir, mocked_makedirs):
        """
        Tests that mkdirs is still successful if directory already
        exists.

        """
        config = {}
        path = '/path/%s/%s' % (self.hostname, self.topic)
        o = FileOutput(config)
        o._mkdirs(path)
        mocked_makedirs.assert_called_with(path)

    @mock.patch(
        'os_code_profiler.outputs.file.os.makedirs',
        side_effect=error_makedirs
    )
    @mock.patch(
        'os_code_profiler.outputs.file.os.path.isdir',
        return_value=False
    )
    def test_mkdirs_other_error(self, mocked_isdir, mocked_makedirs):
        """
        Tests that mkdirs raises OSError if not related to directory
        already existing.

        """
        config = {}
        path = '/path/%s/%s' % (self.hostname, self.topic)
        o = FileOutput(config)
        with self.assertRaises(OSError):
            o._mkdirs(path)

    def test_filename(self):
        """
        Filename should be started_to_ended_pid

        """
        config = {}
        ctx = self.create_ctx()
        o = FileOutput(config)
        name = o._filename(ctx)
        self.assertEquals(
            name,
            "%s_to_%s_%s.stats" % (self.started_string, self.ended_string, self.pid)
        )

    def test_write(self):
        """
        Tests for the write method

        """
        class FakeStats(object):
            pass

        stats = FakeStats()
        stats.save = mock.Mock()

        config = {}
        ctx = self.create_ctx()
        o = FileOutput(config)
        o.write(ctx, stats)

        stats.save.assert_called_with('%s/%s/%s/%s_to_%s_%s.stats' % (
            '/var/log/os_code_profiler',
            self.hostname,
            self.topic,
            self.started_string,
            self.ended_string,
            self.pid
        ))
