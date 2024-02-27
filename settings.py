import logging
import os

LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "DEBUG").upper())

logging.basicConfig(format="%(asctime)s | %(name)24s | %(levelname)8s | %(message)s", level=LOG_LEVEL)

DEV_HOST = os.getenv("DEV_HOST", "localhost")
DEV_PORT = int(os.getenv("DEV_PORT", "9000"))

AMQP_USER = os.getenv("AMQP_USER", "guest")
AMQP_PASSWORD = os.getenv("AMQP_PASSWORD", "guest")
AMQP_HOST = os.getenv("AMQP_HOST", "localhost")
AMQP_PORT = os.getenv("AMQP_PORT", "5672")
AMQP_DSN = os.getenv("AMQP_DSN", f"amqp://{AMQP_USER}:{AMQP_PASSWORD}@{AMQP_HOST}:{AMQP_PORT}//")

KEYVAULT_URI = os.getenv("KEYVAULT_URI", None)
