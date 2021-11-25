import logging

from environment import env_var, read_env

read_env()

LOG_LEVEL = getattr(logging, env_var("LOG_LEVEL", "DEBUG").upper())

logging.basicConfig(format="%(asctime)s | %(name)24s | %(levelname)8s | %(message)s", level=LOG_LEVEL)

DEV_HOST = env_var("DEV_HOST", "0.0.0.0")
DEV_PORT = int(env_var("DEV_PORT", "9000"))

AMQP_USER = env_var("AMQP_USER", "guest")
AMQP_PASSWORD = env_var("AMQP_PASSWORD", "guest")
AMQP_HOST = env_var("AMQP_HOST", "localhost")
AMQP_PORT = env_var("AMQP_PORT", "5672")
AMQP_DSN = env_var("AMQP_DSN", f"amqp://{AMQP_USER}:{AMQP_PASSWORD}@{AMQP_HOST}:{AMQP_PORT}//")

KEYVAULT_URI = env_var("KEYVAULT_URI", None)
