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
    PROJECT = os.getenv("PROJECT", "Bonemarrow")
    PAGE_ICON = os.getenv("PAGE_ICON", "👋")
    DEFAULT_DOTSIZE_NEG = os.getenv("DEFAULT_DOTSIZE_NEG", 3)
    DEFAULT_DOTSIZE_POS = os.getenv("DEFAULT_DOTSIZE_POS", 5)
    DEFAULT_PAGE_SIZE = os.getenv("DEFAULT_PAGE_SIZE", 30)
    DEFAULT_PAGE = os.getenv("DEFAULT_PAGE", 0)
    DEFAULT_SLIDER_VALUE = os.getenv("DEFAULT_SLIDER_VALUE", 0.5)
    DEFAULT_SLIDER_STEPSIZE = os.getenv("DEFAULT_SLIDER_STEPSIZE", 0.05)
    DEFAULT_UPPER_QUANTILE = os.getenv("DEFAULT_UPPER_QUANTILE", 0.998)
    DEFAULT_LOWER_QUANTILE = os.getenv("DEFAULT_LOWER_QUANTILE", 0.990)
    
class Plot:
    X_RANGE_MIN = os.getenv("X_RANGE_MIN", None)
    X_RANGE_MAX = os.getenv("X_RANGE_MAX", None)
    Y_RANGE_MIN = os.getenv("Y_RANGE_MIN", None)
    Y_RANGE_MAX = os.getenv("Y_RANGE_MAX", None)
