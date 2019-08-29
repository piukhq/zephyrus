from environment import env_var, read_env

read_env()

DEV_HOST = env_var("DEV_HOST", "0.0.0.0")
DEV_PORT = int(env_var("DEV_PORT", "5000"))

HERMES_URL = env_var("HERMES_URL", "http://127.0.0.1:8000")
SERVICE_API_KEY = env_var("SERVICE_API_KEY", "F616CE5C88744DD52DB628FAD8B3D")
VISA_CREDENTIALS = {"username": env_var("VISA_USERNAME"), "password": env_var("VISA_PASSWORD")}

REDIS_URL = "redis://:{password}@{host}:{port}/{db}".format(
    password=env_var("REDIS_PASSWORD", ""),
    host=env_var("REDIS_HOST", "localhost"),
    port=env_var("REDIS_PORT", "6379"),
    db=env_var("REDIS_DB", "8"),
)

# Minimum number of minutes before redis cache can be updated by hermes
CLIENT_INFO_STORAGE_TIMEOUT = env_var("CLIENT_INFO_STORAGE_TIMEOUT", 60)

SIGNATURE_SECRET = env_var("SIGNATURE_SECRET", "EL411REgqoW8q-Z8ncZ0m88bkxL9CQfRHT4sSHOJ0RE")

AZURE_ACCOUNT_NAME = env_var("AZURE_ACCOUNT_NAME", "bink")
AZURE_ACCOUNT_KEY = env_var("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = env_var("AZURE_CONTAINER", "dev-media")
AZURE_CERTIFICATE_FOLDER = env_var("AZURE_CERTIFICATE_FOLDER", "zephyrus/certificates/")
MASTERCARD_CERTIFICATE_BLOB_NAME = env_var("MASTERCARD_CERTIFICATE_BLOB_NAME", "mc_perm_cert")

SENTRY_DSN = env_var("SENTRY_DSN")

AMQP_QUEUE = env_var("AMQP_QUEUE", "auth-transactions")
AMQP_USER = env_var("AMQP_QUEUE", "guest")
AMQP_PASSWORD = env_var("AMQP_QUEUE", "guest")
AMQP_HOST = env_var("AMQP_QUEUE", "localhost")
AMQP_PORT = env_var("AMQP_PORT", "5672")
AMQP_DSN = f"amqp://{AMQP_USER}:{AMQP_PASSWORD}@{AMQP_HOST}:{AMQP_PORT}//"
