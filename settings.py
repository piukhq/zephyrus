import os

from dotenv import load_dotenv

load_dotenv()

DEV_HOST = os.getenv('DEV_HOST', '0.0.0.0')
DEV_PORT = os.getenv('DEV_PORT', '5000')
