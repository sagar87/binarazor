import os

from dotenv import load_dotenv

load_dotenv(".env")


class Database:
    HOST = os.environ.get("MONGODB_SERVER")
    PORT = int(os.environ.get("MONGODB_PORT"))
    USERNAME = os.environ.get("MONGO_ROOT_USER")
    PASSWORD = os.environ.get("MONGO_ROOT_PASSWORD")


class Bucket:
    AWS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_KEY_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_URL = os.getenv("AWS_URL")
    AWS_PATH = os.getenv("AWS_PATH")

class App:
    ENV = os.getenv("ENV")
    