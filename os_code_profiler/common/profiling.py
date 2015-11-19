import os
import socket

import utils


class ConfigException(Exception):
    """Simple config exception"""
    pass


class Config():
    """
    Configuration object for setting up profiling.

    """

    valid_clock_types = ['cpu', 'wall']

    def __init__(self, config_dict):
        """
        Inits the config object

        @param config_dict - Dictionary

        """
        self.clock_type = config_dict.get('clock_type', 'wall')
        self.clock_type = str(self.clock_type).lower()
        if self.clock_type not in self.valid_clock_types:
            raise ConfigException("clock_type must be cpu|wall")

        self.interval = int(config_dict.get("interval", 60 * 5))
        self.clear_each_interval = \
            bool(config_dict.get('clear_each_interval', True))


class Context():
    """
    Class for recording profiling information such as:

    hostname - many possible nodes in cluster
    pid - many similar processes on a node
    topic - many kinds of services on a node
    start_timestamp_utc - in seconds
    end_timestamp_utc - in seconds

    Also provides a way to store others.

    """
    def __init__(
        self, hostname=None, pid=None,
        started=None, ended=None, topic=None
    ):
        if hostname is None:
            hostname = socket.gethostname()
        self.hostname = hostname

        if pid is None:
            pid = os.getpid()
        self.pid = pid

        if started is None:
            started = utils.utc_seconds()
        self.started = started

        if ended is None:
            ended = utils.utc_seconds()
        self.ended = ended

        if topic is None:
            topic = "unknown"
        self.topic = topic
