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
    DEFAULT_DOTSIZE_NEG = os.getenv("DEFAULT_DOTSIZE_NEG", 2)
    DEFAULT_DOTSIZE_POS = os.getenv("DEFAULT_DOTSIZE_POS", 5)
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 30))
    DEFAULT_PAGE = int(os.getenv("DEFAULT_PAGE", 0))
    DEFAULT_SLIDER_VALUE = os.getenv("DEFAULT_SLIDER_VALUE", 0.5)
    DEFAULT_SLIDER_STEPSIZE = os.getenv("DEFAULT_SLIDER_STEPSIZE", 0.05)
    DEFAULT_UPPER_QUANTILE = os.getenv("DEFAULT_UPPER_QUANTILE", 0.998)
    DEFAULT_LOWER_QUANTILE = os.getenv("DEFAULT_LOWER_QUANTILE", 0.990)
    DEFAULT_SCALE = int(os.getenv("DEFAULT_SCALE", 8))


class Vars:
    _REVIEWER = "_reviewer"
    REVIEWER = "reviewer"
    _CHANNEL = "_channel"
    CHANNEL = "channel"
    _DOTSIZE_NEG = "_dotsize_neg"
    DOTSIZE_NEG = "dotsize_neg"
    _DOTSIZE_POS = "_dotsize_pos"
    DOTSIZE_POS = "dotsize_pos"
    _POSITIVE = "positive"
    POSITIVE = "positive"

    _PAGE = "_page"
    PAGE = "page"
    _SAMPLES = "_samples"
    SAMPLES = "samples"

    STATISTICS = "statistics"

    _LOWER_QUANTILE = "_lower_quantile"
    LOWER_QUANTILE = "lower_quantile"
    _UPPER_QUANTILE = "upper_quantile"
    UPPER_QUANTILE = "upper_quantile"
    _SLIDER = "_slider"
    SLIDER = "slider"

    _STATUS = "_status"
    STATUS = "status"

    _NUM_SAMPLES = "_num_samples"
    NUM_SAMPLES = "num_samples"

    _NUM_PAGES = "_NUM_PAGES"
    NUM_PAGES = "NUM_PAGES"

    ALL = "all"
    BAD = "bad"
    UNSURE = "unsure"
    NOT_REVIEWED = "not reviewed"
    REVIEWED = "reviewed"
