import logging

from .api import create_app  # noqa

__version__ = "1.10.0"

# Quieten the azure library
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("amqp").setLevel(logging.INFO)
