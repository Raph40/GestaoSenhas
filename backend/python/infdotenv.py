import os
from dotenv import load_dotenv

load_dotenv()  # Loads data from .env into environment variables

host = os.getenv("host")
user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")
