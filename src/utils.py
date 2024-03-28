import os

from dotenv import load_dotenv

load_dotenv(".env")

HTML_PATH = os.getenv("HTML_PATH")


def read_html():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    ) as fh:
        return fh.read()
