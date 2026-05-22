import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

URL = os.getenv("API_URL")
token = os.getenv("API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

DB_URL_CONNECT = os.getenv("DB_URL_CONNECT")

CH_PWD = os.getenv("CH_PWD")
CH_LOGIN = os.getenv("CH_LOGIN")
CH_PORT = os.getenv("CH_PORT")
CH_HOST = os.getenv("CH_HOST")
CH_SSL_ROOT = os.getenv("CH_SSL_ROOT")

OBJECT_STORAGE_BUCKET = os.getenv('OBJECT_STORAGE_BUCKET')
OBJECT_STORAGE_ENDPOINT = os.getenv('OBJECT_STORAGE_ENDPOINT')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

APP_PASSWORD = os.getenv('APP_PASSWORD')

proxy = os.getenv('PROXY')
