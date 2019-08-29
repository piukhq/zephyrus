from setuptools import setup, find_packages

from app import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="zephyrus",
    version=__version__,
    description="Microservice to process auth transactions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["."] + find_packages(),
    url="https://git.bink.com/Olympus/zephyrus",
    author="Chris Latham",
    author_email="cl@bink.com",
    classifiers=("Programming Language :: Python :: 3",),
    zip_safe=True,
)
