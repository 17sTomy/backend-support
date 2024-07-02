from pymongo import MongoClient
from datetime import datetime
from django.conf import settings


class MongoCommands:
    def __init__(self) -> None:
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client["support"]

    def get_db(self):
        return self.client["support"]

    def insert_into_db(self, file_name, audio_url):
        actual_fecha = datetime.now()
        fecha = actual_fecha.date()
        fecha = fecha.isoformat()
        calls_collection = self.db["calls"]

        call_document = {
            "filename": file_name,
            "url": audio_url,
            "date": fecha,
            "estado": "Pendiente",
        }
        calls_collection.insert_one(call_document)

    def get_all_calls(self):
        calls_collection = self.db["calls"]
        return list(calls_collection.find())

    def get_all_detailed_results(self):
        detailed_result_collection = self.db["detailed_result"]
        return list(detailed_result_collection.find())

    def get_all_summary_results(self):
        self.db = self.client["support"]
        summary_result_collection = self.db["summary_result"]
        documents = list(summary_result_collection.find())
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return documents


a = MongoCommands()
print(a.get_all_summary_results())
print(a.get_all_detailed_results())
