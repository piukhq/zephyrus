import jose.jwt
import requests  # noqa

from unittest import mock
from falcon.testing import TestCase
from freezegun import freeze_time
from shared_config_storage.vault.secrets import VaultError  # noqa
from app import create_app
from app.security import generate_jwt, load_secrets


class TestJwtAuth(TestCase):
    TESTING = True
    headers = {"Authorization": "token edfe"}
    payload = {"client_id": "testid", "client_secret": "testsecret"}

    amex_auth_end_point = "/auth_transactions/authorize"
    amex_endpoint = "/auth_transactions/amex"

    def setUp(self):
        super(TestJwtAuth, self).setUp()
        self.app = create_app()

    """
    freeze_time allows anything using a python datetime function to be fixed. This allows testing of the JWT
    token which uses a time stamp for expiry. Since the time is fixed we can compare the test token against what
    is actually generated running the test.
    """

    @mock.patch("app.security.load_secrets")
    @freeze_time("2020-02-21")
    def test_auth_endpoint_success(self, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "testid", "secret": "testsecret"}}

        resp = self.simulate_post(self.amex_auth_end_point, json=self.payload, headers={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json["api_key"],
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1ODIyNDM1MDAsIm5iZiI6MTU4MjI0MzIwMCwiaXNzIjoiYmluayIsImF1ZCI6Imh0dHBzOi8vYXBpLmJpbmsuY29tIiwiaWF0IjoxNTgyMjQzMjAwLCJzdWIiOiJ0ZXN0aWQifQ.irf-CKuXMCs071vfTZPfjTXIafLytQzts9DXHTJWzUs",
        )  # noqa

    @mock.patch("app.security.load_secrets")
    def test_auth_endpoint_fails_missing_params(self, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}
        payload_error = {"client_id": "", "client_secret": "testsecret"}
        resp = self.simulate_post(self.amex_auth_end_point, json=payload_error, headers={})
        self.assertEqual(resp.status_code, 400)

    @mock.patch("app.security.load_secrets")
    @freeze_time("2020-02-21")
    def test_generate_jwt(self, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "testid", "secret": "testsecret"}}
        token = generate_jwt("amex")

        jwt = jose.jwt.decode(token, "testsecret", audience="https://api.bink.com", issuer="bink")

        self.assertEqual(jwt["sub"], "testid")

    @mock.patch("app.security.load_secrets")
    @freeze_time("2020-02-21")
    def test_generate_jwt_error(self, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}
        token = generate_jwt("amex")

        self.assertEqual(token, None)

    @mock.patch("app.security.read_vault", autospec=True)
    def test_load_secrets(self, mock_read_vault):
        mock_read_vault.return_value = {"amex": {"client_id": "testid", "secret": "testsecret"}}
        secret = load_secrets()
        self.assertTrue(mock_read_vault.called)
        self.assertEqual(secret["amex"]["client_id"], "testid")

    # @mock.patch("app.security.read_vault", autospec=True)
    # def test_load_secrets_exception(self, mock_read_vault):
    #     mock_read_vault.side_effect = requests.exceptions.RequestException
    #     with self.assertRaises(VaultError) as cm:
    #         resp = load_secrets()

    @mock.patch("app.amex.authentication.load_secrets")
    @mock.patch("app.amex.authentication.jose.jwt.decode", autospec=True)
    def test_auth_decorator_success(self, mock_decode, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertEqual(resp.status_code, 200)

    @mock.patch("app.amex.authentication.load_secrets")
    def test_auth_decorator_fails_missing_header(self, mock_load_secrets):
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}
        resp = self.simulate_post(self.amex_endpoint, json=self.payload)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json["name"], "MISSING_AUTH")

    @mock.patch("app.amex.authentication.load_secrets")
    def test_auth_decorator_fails_wrong_format(self, mock_load_secrets):
        headers = {"Authorization": "badformat"}
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}
        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json["name"], "INVALID_AUTH_FORMAT")

    @mock.patch("app.amex.authentication.load_secrets")
    def test_auth_decorator_fails_wrong_prefix(self, mock_load_secrets):
        headers = {"Authorization": "nottoken sdfsdf"}
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json["name"], "INVALID_AUTH_TYPE")

    @mock.patch("app.amex.authentication.load_secrets")
    @mock.patch("app.amex.authentication.jose.jwt.decode", autospec=True)
    def test_auth_decorator_fails_expired_signature(self, mock_decode, mock_load_secrets):
        mock_decode.side_effect = jose.exceptions.ExpiredSignatureError
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json["name"], "AUTH_EXPIRED")

    @mock.patch("app.amex.authentication.load_secrets")
    @mock.patch("app.amex.authentication.jose.jwt.decode", autospec=True)
    def test_auth_decorator_fails_invalid_signature(self, mock_decode, mock_load_secrets):
        mock_decode.side_effect = jose.exceptions.JWTError
        mock_load_secrets.return_value = {"amex": {"client_id": "", "secret": "testsecret"}}

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json["name"], "INVALID_AUTH_TOKEN")
