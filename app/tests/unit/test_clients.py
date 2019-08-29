import json
from unittest import mock
from unittest.mock import MagicMock

import redis
import requests
from falcon.testing import TestCase
from redis import StrictRedis

from app import create_app
from app.clients import ClientInfo, redis_store
from app.errors import CustomException


class TestClientAppInfo(TestCase):
    TESTING = True
    clients = [
        {"client_id": "12eds", "secret": "edr45", "organisation": "Amex"},
        {"client_id": "ghtrge", "secret": "hrfere", "organisation": "Master Card"},
    ]

    def setUp(self):
        super(TestClientAppInfo, self).setUp()
        self.app = create_app()

    @mock.patch("app.clients.redis_store.get", autospec=True)
    def test_storage_handler_catches_connection_errors(self, mock_redis_get):
        mock_redis_get.side_effect = redis.exceptions.ConnectionError
        with self.assertRaises(CustomException) as e:
            ClientInfo._redis_handler(redis_store.get, "some_key")

        self.assertTrue(mock_redis_get.called)
        self.assertEqual(e.exception.name, "CONNECTION_ERROR")

    @mock.patch("settings.CLIENT_INFO_STORAGE_TIMEOUT", 100)
    @mock.patch("time.time", autospec=True)
    @mock.patch.object(ClientInfo, "_get")
    def test_is_stale_is_false_if_timeout_not_exceeded(self, mock_get_clients_last_saved, mock_time):
        mock_get_clients_last_saved.return_value = "12345.34"
        mock_time.return_value = 12555.34

        result = ClientInfo.is_stale()

        self.assertFalse(result)

    @mock.patch("settings.CLIENT_INFO_STORAGE_TIMEOUT", 1)
    @mock.patch("time.time", autospec=True)
    @mock.patch.object(ClientInfo, "_get")
    def test_is_stale_is_true_when_timeout_is_exceeded(self, mock_get_clients_last_saved, mock_time):
        mock_get_clients_last_saved.return_value = "12345.34"
        mock_time.return_value = 12555.34

        result = ClientInfo.is_stale()

        self.assertTrue(result)

    @mock.patch("settings.CLIENT_INFO_STORAGE_TIMEOUT", 100)
    @mock.patch("time.time", autospec=True)
    @mock.patch.object(ClientInfo, "_get")
    def test_is_stale_is_true_if_there_is_no_last_saved_record(self, mock_get_clients_last_saved, mock_time):
        mock_get_clients_last_saved.return_value = None
        mock_time.return_value = 12555.34

        result = ClientInfo.is_stale()

        self.assertTrue(result)

    @mock.patch.object(StrictRedis, "get")
    def test_get_client_retrieves_client_information(self, mock_redis_get):
        mock_redis_get.return_value = json.dumps(self.clients[0]).encode("utf8")

        result = ClientInfo.get_client(self.clients[0]["client_id"])

        self.assertEqual(result, self.clients[0])
        self.assertTrue(mock_redis_get.called)

    @mock.patch.object(StrictRedis, "get")
    def test_get_client_raises_exception_on_missing_client(self, mock_redis_get):
        mock_redis_get.return_value = None

        with self.assertRaises(CustomException) as e:
            ClientInfo.get_client("missingClientId")

        self.assertTrue(mock_redis_get.called)
        self.assertEqual(e.exception.name, "CLIENT_DOES_NOT_EXIST")

    @mock.patch("app.clients.redis_store.set", autospec=True)
    @mock.patch("requests.get", autospec=True)
    @mock.patch.object(ClientInfo, "is_stale")
    def test_update_client_apps_success(self, mock_is_stale, mock_request, mock_redis_set):
        mock_is_stale.return_value = True

        request = MagicMock()
        request.json.return_value = self.clients
        mock_request.return_value = request

        c = ClientInfo()

        self.assertEqual(c.data, self.clients)
        self.assertTrue(mock_is_stale.called)
        self.assertTrue(mock_request.called)
        self.assertTrue(mock_redis_set.called)

    @mock.patch("app.clients.redis_store.set", autospec=True)
    @mock.patch("requests.get", autospec=True)
    @mock.patch.object(ClientInfo, "is_stale")
    def test_update_client_raises_custom_exception_on_connection_error(
        self, mock_is_stale, mock_request, mock_redis_set
    ):
        mock_is_stale.return_value = True

        mock_request.side_effect = requests.ConnectionError

        with self.assertRaises(CustomException) as e:
            ClientInfo()

        self.assertTrue(mock_is_stale.called)
        self.assertTrue(mock_request.called)
        self.assertFalse(mock_redis_set.called)
        self.assertEqual(e.exception.name, "CONNECTION_ERROR")

    @mock.patch("app.clients.redis_store.set", autospec=True)
    @mock.patch("requests.get", autospec=True)
    @mock.patch.object(ClientInfo, "is_stale")
    def test_update_client_raises_exception_on_unexpected_response(self, mock_is_stale, mock_request, mock_redis_set):
        mock_is_stale.return_value = True

        request = MagicMock()
        request.json.return_value = [{"bad": "schema"}, {"no": "good"}]
        mock_request.return_value = request

        with self.assertRaises(CustomException) as e:
            ClientInfo()

        self.assertTrue(mock_is_stale.called)
        self.assertTrue(mock_request.called)
        self.assertFalse(mock_redis_set.called)
        self.assertEqual(e.exception.name, "CONNECTION_ERROR")
