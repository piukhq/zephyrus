import logging
from typing import Optional, Tuple

import opentracing
from kombu import Connection

import settings

log = logging.getLogger(__name__)


def _on_error(exc, interval):
    log.warning(f"Failed to connect to RabbitMQ: {exc}. Will retry after {interval:.1f}s...")


def add(message: dict, *, provider: str, queue_name: str, span: Optional[opentracing.Span] = None) -> None:
    headers: dict[str, str] = {}
    if span:
        settings.tracer.inject(span, opentracing.Format.TEXT_MAP, headers)
    headers["X-Provider"] = provider

    with Connection(settings.AMQP_DSN, connect_timeout=3) as conn:
        conn.ensure_connection(
            errback=_on_error, max_retries=3, interval_start=0.2, interval_step=0.4, interval_max=1, timeout=3
        )
        q = conn.SimpleQueue(queue_name)

        q.put(message, headers=headers)


def is_available() -> Tuple[bool, str]:
    status, error_msg = True, ""

    try:
        with Connection(settings.AMQP_DSN, connect_timeout=3) as conn:
            conn.connect()
            assert conn.connected
    except Exception as err:
        status = False
        error_msg = f"Failed to connect to queue, err: {err}"

    return status, error_msg
