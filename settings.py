import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

DEV_HOST = os.getenv('DEV_HOST', '0.0.0.0')
DEV_PORT = os.getenv('DEV_PORT', '5000')
