import logging

from .api import create_app  # noqa

__version__ = "1.9"

# Quieten the azure library
logging.getLogger("azure").setLevel(logging.WARNING)
# Quieten the amqp library
logging.getLogger("amqp").setLevel(logging.INFO)
