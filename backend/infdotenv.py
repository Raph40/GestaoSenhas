import os
from dotenv import load_dotenv

load_dotenv()  # Loads data from .env into environment variables

host = os.getenv("DB_HOST", "127.0.0.1")
user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")