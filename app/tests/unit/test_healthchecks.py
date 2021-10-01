from unittest import mock

from falcon.testing import TestCase

from app import create_app


class TestHealthchecks(TestCase):
    TESTING = True

    def setUp(self):
        super(TestHealthchecks, self).setUp()
        self.app = create_app()

    def test_metrics(self):
        resp = self.simulate_get("/metrics")
        self.assertEqual(resp.status_code, 200)

    def test_healthz(self):
        resp = self.simulate_get("/healthz")
        self.assertEqual(resp.status_code, 200)

    def test_livez(self):
        resp = self.simulate_get("/livez")
        self.assertEqual(resp.status_code, 204)

    @mock.patch("app.queue.is_available")
    def test_readyz_queue_up(self, queue_mock):
        queue_mock.return_value = True, ""

        resp = self.simulate_get("/readyz")
        self.assertEqual(resp.status_code, 204)

    @mock.patch("app.queue.is_available")
    def test_readyz_queue_down(self, queue_mock):
        queue_mock.return_value = False, "blah"

        resp = self.simulate_get("/readyz")
        self.assertEqual(resp.status_code, 500)
