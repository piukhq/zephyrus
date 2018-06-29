from setuptools import setup

from app.version import __version__

setup(
    name='zephyrus',
    version=__version__,
    description='Microservice to process auth transactions.',
    url='https://git.bink.com/Olympus/zephyrus',
    author='Chris Latham',
    author_email='cl@bink.com',
    zip_safe=True)
