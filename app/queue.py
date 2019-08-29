from kombu import Connection

import settings


def add(message: dict, *, provider: str) -> None:
    with Connection(settings.AMQP_DSN) as conn:
        q = conn.SimpleQueue(settings.AMQP_QUEUE)
        q.put(message, headers={"X-Provider": provider})
