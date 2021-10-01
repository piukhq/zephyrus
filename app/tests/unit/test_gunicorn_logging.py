import logging

import pytest

import gunicorn_logger


@pytest.mark.parametrize(
    "logline,should_log",
    [
        ("GET /livez HTTP/1.1", False),
        ("GET /metrics HTTP/1.1", False),
        ("POST /auth_transactions/visa HTTP/1.1", True),
    ],
)
def test_log_filtering(logline, should_log):
    log_filter = gunicorn_logger.HealthcheckFilter("filter")
    log_record = logging.LogRecord("name", logging.INFO, "/", 1, logline, {}, None)

    assert log_filter.filter(log_record) is should_log
