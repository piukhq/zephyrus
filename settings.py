import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

DEV_HOST = os.getenv('DEV_HOST', '0.0.0.0')
DEV_PORT = os.getenv('DEV_PORT', '5000')

HERMES_URL = os.getenv('HERMES_URL', 'http://127.0.0.1:8000')
SERVICE_API_KEY = os.getenv('SERVICE_API_KEY', 'F616CE5C88744DD52DB628FAD8B3D')

REDIS_URL = os.getenv('ZEPHYRUS_REDIS_URL', 'redis://localhost:6379/8')

CLIENT_INFO_STORAGE_TIMEOUT = 60    # Minimum number of minutes before redis cache can be updated by hermes

SIGNATURE_SECRET = os.getenv('SIGNATURE_SECRET', 'EL411REgqoW8q-Z8ncZ0m88bkxL9CQfRHT4sSHOJ0RE')

MASTERCARD_TRANSACTION_SIGNING_CERTIFICATE = None
MASTERCARD_CERTIFICATE_COMMON_NAME = ""