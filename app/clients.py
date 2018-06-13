import json
import time

import redis
import requests

import settings
from app import redis_store
from app.errors import CONNECTION_ERROR, CustomException
from settings import HERMES_URL, SERVICE_API_KEY


class ClientInfo:
    data = None

    def __init__(self):
        if self.is_stale():
            self.data = self.update_client_apps()
            self._set_clients_last_saved()

    def update_client_apps(self):
        url = f'{HERMES_URL}/payment_cards/client_apps'

        try:
            resp = requests.get(url, headers={'Authorization': f'token {SERVICE_API_KEY}'})
            data = resp.json()
            # TODO: validate response. (format, correct keys etc.)

            self._set_clients(data)
        except requests.RequestException as e:
            raise CustomException(CONNECTION_ERROR, message="Error retrieving client information.") from e

        self._set_clients_last_saved()
        return data

    @staticmethod
    def is_stale():
        try:
            stored_timestamp = float(redis_store.get(f"auth-transactions:clients-last-saved"))
            current_timestamp = time.time()

            return (current_timestamp - stored_timestamp) > (settings.CLIENT_INFO_STORAGE_TIMEOUT * 60)
        except TypeError:
            return True
        except redis.exceptions.ConnectionError as e:
            raise CustomException(CONNECTION_ERROR, message="Error connecting to Redis.") from e

    @staticmethod
    def get_client(client_id):
        client = redis_store.get(f"auth-transactions:{client_id}")
        return json.loads(client.decode('utf-8'))

    @staticmethod
    def _set_clients(clients):
        """
        Stores client information for quick access with the client id.
        :param clients: List of dicts e.g [{'client_id': '123sd', 'client_secret: '1qa1', 'organisation': 'Amex
        '"""
        for client in clients:
            redis_store.set(f"auth-transactions:{client['client_id']}", json.dumps(client))

        return True

    @staticmethod
    def _set_clients_last_saved():
        timestamp = time.time()
        redis_store.set(f"auth-transactions:clients-last-saved", timestamp)


