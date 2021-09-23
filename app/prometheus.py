from os import getenv

import falcon
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, Counter, generate_latest, multiprocess

counter = Counter("payment_card_total", "Total requests", ["payment_card", "type"])


class PrometheusHandler:
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        registry = REGISTRY

        if getenv("PROMETHEUS_MULTIPROC_DIR"):
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)

        resp.set_header("Content-Type", CONTENT_TYPE_LATEST)
        resp.data = generate_latest(registry)
        resp.status = falcon.HTTP_200
