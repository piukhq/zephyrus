import json
import time

import redis
import requests
import voluptuous

import settings
from app import schema
from app.errors import CONNECTION_ERROR, CustomException, CLIENT_DOES_NOT_EXIST
from settings import HERMES_URL, SERVICE_API_KEY

redis_store = redis.Redis(settings.REDIS_URL)


class ClientInfo:
    data = None

    def __init__(self):
        if self.is_stale():
            self.data = self.update_client_apps()

    def update_client_apps(self):
        url = f'{HERMES_URL}/payment_cards/client_apps'
        try:
            resp = requests.get(url, headers={'Authorization': f'token {SERVICE_API_KEY}'})

            # Validate response data
            data = resp.json()
            schema.client_info_list(data)

            self._set_clients(data)
        except requests.RequestException as e:
            raise CustomException(CONNECTION_ERROR, message="Error retrieving client information.") from e
        except voluptuous.error.Invalid as e:
            raise CustomException(CONNECTION_ERROR) from e

        self._set_clients_last_saved()
        return data

    @staticmethod
    def is_stale():
        try:
            stored_timestamp = float(ClientInfo._get(f"auth-transactions:clients-last-saved"))
            current_timestamp = time.time()

            return (current_timestamp - stored_timestamp) > (settings.CLIENT_INFO_STORAGE_TIMEOUT * 60)
        except TypeError:
            return True

    @staticmethod
    def get_client(client_id):
        try:
            client = ClientInfo._get(f"auth-transactions:{client_id}")
            client_data = json.loads(client.decode('utf-8'))
        except AttributeError as e:
            raise CustomException(CLIENT_DOES_NOT_EXIST) from e

        return client_data

    @staticmethod
    def _set_clients(clients):
        """
        Stores client information for quick access with the client id.
        :param clients: List of dicts e.g [{'client_id': '123sd', 'client_secret: '1qa1', 'organisation': 'Amex'}]
        """
        for client in clients:
            ClientInfo._set(f"auth-transactions:{client['client_id']}", json.dumps(client))
        return True

    @staticmethod
    def _set_clients_last_saved():
        timestamp = time.time()
        ClientInfo._set(f"auth-transactions:clients-last-saved", timestamp)

    @staticmethod
    def _redis_handler(func, *args):
        try:
            return func(*args)
        except redis.exceptions.ConnectionError as e:
            raise CustomException(CONNECTION_ERROR, message="Error connecting to Redis.") from e

    @staticmethod
    def _get(key):
        return ClientInfo._redis_handler(redis_store.get, key)

    @staticmethod
    def _set(key, val):
        ClientInfo._redis_handler(redis_store.set, key, val)
        return True
