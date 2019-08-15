from environment import env_var, read_env

read_env()

DEV_HOST = env_var('DEV_HOST', '0.0.0.0')
DEV_PORT = int(env_var('DEV_PORT', '5000'))

HERMES_URL = env_var('HERMES_URL', 'http://127.0.0.1:8000')
SERVICE_API_KEY = env_var('SERVICE_API_KEY', 'F616CE5C88744DD52DB628FAD8B3D')
VISA_CREDENTIALS = {
    'username': env_var('VISA_USERNAME'),
    'password': env_var('VISA_PASSWORD')
}

REDIS_URL = 'redis://:{password}@{host}:{port}/{db}'.format(
    password=env_var('REDIS_PASSWORD', ''),
    host=env_var('REDIS_HOST', 'localhost'),
    port=env_var('REDIS_PORT', '6379'),
    db=env_var('REDIS_DB', '8')
)

# Minimum number of minutes before redis cache can be updated by hermes
CLIENT_INFO_STORAGE_TIMEOUT = env_var('CLIENT_INFO_STORAGE_TIMEOUT', 60)

SIGNATURE_SECRET = env_var('SIGNATURE_SECRET', 'EL411REgqoW8q-Z8ncZ0m88bkxL9CQfRHT4sSHOJ0RE')

AZURE_ACCOUNT_NAME = env_var('AZURE_ACCOUNT_NAME', 'bink')
AZURE_ACCOUNT_KEY = env_var('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = env_var('AZURE_CONTAINER', 'dev-media')
AZURE_CERTIFICATE_FOLDER = env_var('AZURE_CERTIFICATE_FOLDER', 'zephyrus/certificates/')
MASTERCARD_CERTIFICATE_BLOB_NAME = env_var('MASTERCARD_CERTIFICATE_BLOB_NAME', 'mc_perm_cert')

SENTRY_DSN = env_var('SENTRY_DSN')

CELERY_QUEUE = env_var('CELERY_QUEUE', 'auth-transactions')
CELERY_BROKER_URI = '{protocol}://{username}:{password}@{host}:{port}//'.format(
    protocol=env_var('CELERY_BROKER_PROTOCOL', 'pyamqp'),
    username=env_var('CELERY_BROKER_USERNAME', 'guest'),
    password=env_var('CELERY_BROKER_PASSWORD', 'guest'),
    host=env_var('CELERY_BROKER_HOST', 'localhost'),
    port=env_var('CELERY_BROKER_PORT', '5672')
)


class CeleryConf:
    celery_broker_url = CELERY_BROKER_URI
    celery_default_queue = CELERY_QUEUE
    celery_task_serializer = 'json'
    celery_result_serializer = 'json'
    celery_accept_content = ['json']
    celery_task_routes = {f'{CELERY_QUEUE}.save': {'queue': CELERY_QUEUE}}
