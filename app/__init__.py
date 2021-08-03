import logging

from .api import create_app  # noqa

__version__ = "1.8"

# Quieten the azure library
logging.getLogger("azure").setLevel(logging.WARNING)
