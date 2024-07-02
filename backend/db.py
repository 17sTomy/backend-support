from pymongo import MongoClient
from dotenv import load_dotenv
import os
from django.conf import settings


def get_db():
    load_dotenv()
    client = MongoClient(settings.MONGODB_URL)
    db = client["support"]
    return db
