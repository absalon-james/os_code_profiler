import datetime
import importlib

epoch = datetime.datetime.utcfromtimestamp(0)


def utc_seconds():
    return (datetime.datetime.now() - epoch).total_seconds()


class PluginLoader(object):
    """
    Simple object loader that returns instances of a named class
    that can be found in the python path.

    """
    def load(self, fullname, config=None):
        """
        Breaks full name into module name and class name.
        Finds the class within a module and returns an instance
        of that class.

        @param fullname - String. ex: "package_name.module_name.class_name"
        @param config - Optional dictionary

        """
        if config is None:
            config = {}
        modulename, classname = fullname.rsplit('.', 1)
        module = importlib.import_module(modulename)
        klass = getattr(module, classname)
        return klass(config)
