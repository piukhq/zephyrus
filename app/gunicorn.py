import logging.config

import gunicorn.glogging


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(s in msg for s in ("/healthz", "/readyz", "/livez", "/metrics"))


class Logger(gunicorn.glogging.Logger):
    def setup(self, *args, **kwargs) -> None:
        super(Logger, self).setup(*args, **kwargs)

        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(HealthcheckFilter())
