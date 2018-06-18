import json
from unittest import mock

import jose
from flask_testing import TestCase

import settings
from app import create_app, CustomException
from app.authentication.amex import generate_jwt
from app.clients import ClientInfo
from app.errors import CLIENT_DOES_NOT_EXIST


class TestJwtAuth(TestCase):
    TESTING = True
    headers = {
        'Authorization': 'token edfe'
    }
    payload = {
        "client_id": "testid",
        "client_secret": "testsecret"
    }

    client_obj = {
        "client_id": "testid",
        "secret": "testsecret",
        "organisation": "The Organisation"
    }

    def create_app(self):
        return create_app(self, )

    @mock.patch('app.authentication.amex.generate_jwt', autospec=True)
    @mock.patch('app.authentication.amex.ClientInfo', autospec=True)
    def test_auth_endpoint_success(self, mock_client_info, mock_gen_jwt):
        mock_client_info.return_value.data = None
        mock_client_info.return_value.get_client.return_value = {
            'client_id': 'testid',
            'secret': 'testsecret'
        }
        mock_gen_jwt.return_value = 'really_bad_jwt'

        resp = self.client.post('/authorize',
                                data=json.dumps(self.payload),
                                content_type='application/json',
                                headers={})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['api_key'], 'really_bad_jwt')

    @mock.patch('app.authentication.amex.generate_jwt', autospec=True)
    @mock.patch('app.authentication.amex.ClientInfo', autospec=True)
    def test_auth_success_with_refreshed_client_apps_info(self, mock_client_info, mock_gen_jwt):
        mock_client_info.return_value.data = [
            {'client_id': 'extra', 'secret': 'extra'},
            {'client_id': 'testid', 'secret': 'testsecret'},
        ]
        mock_gen_jwt.return_value = 'really_bad_jwt'
        resp = self.client.post('/authorize',
                                data=json.dumps(self.payload),
                                content_type='application/json',
                                headers={})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['api_key'], 'really_bad_jwt')

    def test_auth_endpoint_fails_missing_params(self):
        payload = self.payload.copy()
        payload.pop('client_secret')

        resp = self.client.post('/authorize',
                                data=json.dumps(payload),
                                content_type='application/json',
                                headers={})

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['name'], 'MISSING_PARAMS')

    @mock.patch('app.authentication.amex.generate_jwt', autospec=True)
    @mock.patch('app.authentication.amex.ClientInfo', autospec=True)
    def test_auth_endpoint_fails_invalid_client(self, mock_client_info, mock_gen_jwt):
        mock_client_info.return_value.data = [
            {'client_id': 'nomatch1', 'secret': 'extra'},
            {'client_id': 'nomatch2', 'secret': 'testsecret'},
        ]
        mock_gen_jwt.return_value = 'really_bad_jwt'
        resp = self.client.post('/authorize',
                                data=json.dumps(self.payload),
                                content_type='application/json',
                                headers={})

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'CLIENT_DOES_NOT_EXIST')

    @mock.patch('app.authentication.amex.generate_jwt', autospec=True)
    @mock.patch('app.authentication.amex.ClientInfo', autospec=True)
    def test_auth_endpoint_fails_invalid_secret(self, mock_client_info, mock_gen_jwt):
        mock_client_info.return_value.data = [
            {'client_id': 'testid', 'secret': 'bad_secret'},
        ]
        mock_gen_jwt.return_value = 'really_bad_jwt'
        resp = self.client.post('/authorize',
                                data=json.dumps(self.payload),
                                content_type='application/json',
                                headers={})

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'INVALID_CLIENT_SECRET')

    @mock.patch.object(ClientInfo, 'get_client')
    @mock.patch('app.authentication.amex.jose.jwt.decode', autospec=True)
    def test_auth_decorator_success(self, mock_decode, mock_get_client):
        mock_get_client.return_value = self.client_obj

        resp = self.client.get('/me', headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertEqual(resp.status_code, 200)

    def test_auth_decorator_fails_missing_header(self):
        resp = self.client.get('/me')

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'MISSING_AUTH')

    def test_auth_decorator_fails_wrong_format(self):
        headers = {
            'Authorization': 'badformat'
        }
        resp = self.client.get('/me', headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'INVALID_AUTH_FORMAT')

    def test_auth_decorator_fails_wrong_prefix(self):
        headers = {
            'Authorization': 'nottoken sdfsdf'
        }

        resp = self.client.get('/me', headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'INVALID_AUTH_TYPE')

    @mock.patch('app.authentication.amex.jose.jwt.decode', autospec=True)
    def test_auth_decorator_fails_expired_signature(self, mock_decode):
        mock_decode.side_effect = jose.exceptions.ExpiredSignatureError

        headers = {
            'Authorization': 'token sdfsdf'
        }

        resp = self.client.get('/me', headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'AUTH_EXPIRED')

    @mock.patch('app.authentication.amex.jose.jwt.decode', autospec=True)
    def test_auth_decorator_fails_invalid_signature(self, mock_decode):
        mock_decode.side_effect = jose.exceptions.JWTError

        headers = {
            'Authorization': 'token sdfsdf'
        }

        resp = self.client.get('/me', headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'INVALID_AUTH_TOKEN')

    @mock.patch.object(ClientInfo, 'get_client')
    @mock.patch('app.authentication.amex.jose.jwt.decode', autospec=True)
    def test_auth_decorator_fails_missing_client_info(self, mock_decode, mock_get_client):
        mock_get_client.side_effect = CustomException(CLIENT_DOES_NOT_EXIST)

        headers = {
            'Authorization': 'token sdfsdf'
        }

        resp = self.client.get('/me', headers=headers)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json['name'], 'CLIENT_DOES_NOT_EXIST')

    def test_generate_jwt(self):

        token = generate_jwt(self.client_obj)

        claims = jose.jwt.decode(
            token,
            key=settings.SIGNATURE_SECRET,
            audience='https://api.bink.com',
            issuer='bink')

        self.assertEqual(claims['sub'], 'testid')
