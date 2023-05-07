# config.py
from dotenv import load_dotenv
import os
from pymodm.connection import connect
import pymongo

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI")

connect(MONGODB_CONNECTION_URI, alias="pymodm-conn")

