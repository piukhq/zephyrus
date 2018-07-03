from environment import env_var, read_env
import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(APP_DIR)
read_env()

DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
DEV_PORT = env_var('DEV_PORT', '5000')

HERMES_URL = env_var('HERMES_URL', 'http://127.0.0.1:8000')
SERVICE_API_KEY = env_var('SERVICE_API_KEY', 'F616CE5C88744DD52DB628FAD8B3D')

REDIS_PASSWORD = env_var('REDIS_PASSWORD', '')
REDIS_HOST = env_var('REDIS_HOST', 'localhost')
REDIS_PORT = env_var('REDIS_PORT', '6379')
REDIS_DB = env_var('REDIS_DB', '8')
REDIS_URL = 'redis://:{password}@{host}:{port}/{db}'.format(**{
    'password': REDIS_PASSWORD,
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB
})

# Minimum number of minutes before redis cache can be updated by hermes
CLIENT_INFO_STORAGE_TIMEOUT = env_var('CLIENT_INFO_STORAGE_TIMEOUT', 60)

SIGNATURE_SECRET = env_var('SIGNATURE_SECRET', 'EL411REgqoW8q-Z8ncZ0m88bkxL9CQfRHT4sSHOJ0RE')

MASTERCARD_SIGNING_CERTIFICATE_AZURE_BLOB_NAME = "mastercard/mc_perm_cert"

AZURE_ACCOUNT_NAME = env_var('ZEPHYRUS_AZURE_ACCOUNT_NAME', 'bink')
AZURE_ACCOUNT_KEY = env_var('ZEPHYRUS_AZURE_ACCOUNT_KEY', '')
AZURE_CERTIFICATE_FOLDER = env_var('ZEPHYRUS_CERTIFICATE_CONTAINER', 'dev-media/zephyrus/certificates')

SENTRY_DSN = env_var('SENTRY_DSN')
