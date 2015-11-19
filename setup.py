from setuptools import setup

long_description = (
    "Collection of tools for collecting code profiling data from various"
    " openstack services."
)

setup(
    name="os_code_profiler",
    version="0.0.0",
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=['os_code_profiler'],
    package_data={'os_code_profiler': ['os_code_profiler/*']},
    long_description=long_description
)
