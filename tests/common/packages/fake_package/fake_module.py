class FakePlugin(object):
    """
    FakeClass for testing the plugin loader

    """
    def __init__(self, config):
        for key, value in config.iteritems():
            setattr(self, key, value)
