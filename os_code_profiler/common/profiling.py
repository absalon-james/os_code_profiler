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
        self.clear_each_interval = bool(config_dict.get('clear_each_interval', True))
        self.results_dir = config_dict.get("results_dir", "/tmp")
