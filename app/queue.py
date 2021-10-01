import logging
from typing import Optional, Tuple

import opentracing
import opentracing.tags as ot_tags
from kombu import Connection

import settings

log = logging.getLogger(__name__)


def _on_error(exc, interval):
    log.warning(f"Failed to connect to RabbitMQ: {exc}. Will retry after {interval:.1f}s...")


def add(
    message: dict,
    *,
    provider: str,
    queue_name: str,
    span: Optional[opentracing.Span] = None,
) -> None:
    headers: dict[str, str] = {"X-Provider": provider}
    child_scope: Optional[opentracing.Scope] = None

    if span:
        child_scope = settings.tracer.start_active_span("queue_add", child_of=span)
        child_scope.span.set_tag(ot_tags.COMPONENT, "Falcon")
        child_scope.span.set_tag("provider", provider)
        child_scope.span.set_tag("queue", queue_name)
        child_scope.span.set_tag(ot_tags.SPAN_KIND, ot_tags.SPAN_KIND_PRODUCER)
        settings.tracer.inject(child_scope.span, opentracing.Format.TEXT_MAP, headers)

    with Connection(settings.AMQP_DSN, connect_timeout=3) as conn:
        conn.ensure_connection(
            errback=_on_error,
            max_retries=3,
            interval_start=0.2,
            interval_step=0.4,
            interval_max=1,
            timeout=3,
        )
        q = conn.SimpleQueue(queue_name)

        q.put(message, headers=headers)

    if child_scope:
        child_scope.close()


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
