import logging
from typing import cast

import opentracing
from jaeger_client import Config

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

_tracing_config = Config(
    config={
        "propagation": "b3",
        "sampler": {
            "type": "probabilistic",
            "param": float(env_var("TRACING_SAMPLE_RATE", "0")),
        },
        "local_agent": {
            "reporting_host": env_var("TRACING_AGENT_HOST", "localhost"),
            # 6831 for jaeger traces, 5775 for b3
            "reporting_port": env_var("TRACING_AGENT_REPORTING_PORT", "5775"),
            "sampling_port": env_var("TRACING_AGENT_SAMPLING_PORT", "5778"),
        },
        "logging": True,
    },
    service_name="zephyrus",
    validate=True,
)

# Casting to stop mypy complaining, it returns a tracer on first run else None
tracer = cast(opentracing.Tracer, _tracing_config.initialize_tracer())
