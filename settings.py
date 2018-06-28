from environment import env_var, read_env

read_env()

DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
DEV_PORT = env_var('DEV_PORT', '5000')

HERMES_URL = env_var('HERMES_URL', 'http://127.0.0.1:8000')
SERVICE_API_KEY = env_var('SERVICE_API_KEY', 'F616CE5C88744DD52DB628FAD8B3D')

REDIS_URL = env_var('ZEPHYRUS_REDIS_URL', 'redis://localhost:6379/8')

CLIENT_INFO_STORAGE_TIMEOUT = 60    # Minimum number of minutes before redis cache can be updated by hermes

SIGNATURE_SECRET = env_var('SIGNATURE_SECRET', 'EL411REgqoW8q-Z8ncZ0m88bkxL9CQfRHT4sSHOJ0RE')

MASTERCARD_TRANSACTION_SIGNING_CERTIFICATE = None
MASTERCARD_CERTIFICATE_COMMON_NAME = ""
