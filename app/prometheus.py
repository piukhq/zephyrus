import logging
import os
import threading
import time
import urllib.error

from prometheus_client import REGISTRY, push_to_gateway, Counter

counter = Counter("payment_card_total", "Total requests", ["payment_card", "type"])


def start_pushgateway_thread(push_gateway: str, prometheus_job: str):
    logging.info("Configuring prometheus metric pusher")
    thread = PrometheusPushThread(push_gateway, prometheus_job)
    thread.daemon = True
    thread.start()
    logging.info("Prometheus push thread started")


class PrometheusPushThread(threading.Thread):
    SLEEP_INTERVAL = 30
    PUSH_TIMEOUT = 3  # PushGateway should be running in the same pod

    def __init__(self, prometheus_push_gateway: str, prometheus_job: str):
        # Grouping key should not need pod id as prometheus
        # should tag that itself
        self.grouping_key = {"pid": str(os.getpid())}
        self.prometheus_push_gateway = prometheus_push_gateway
        self.prometheus_job = prometheus_job
        super().__init__()

    def run(self):
        time.sleep(10)
        while True:
            try:
                push_to_gateway(
                    gateway=self.prometheus_push_gateway,
                    job=self.prometheus_job,
                    registry=REGISTRY,
                    grouping_key=self.grouping_key,
                    timeout=self.PUSH_TIMEOUT,
                )
                logging.debug("Pushed metrics to gateway")
            except (ConnectionRefusedError, urllib.error.URLError):
                logging.warning("Failed to push metrics, connection refused")
            except Exception as err:
                logging.exception("Caught exception whilst posting metrics", exc_info=err)

            time.sleep(self.SLEEP_INTERVAL)
