from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from django.conf import settings


class MongoCommands():
    def __init__(self) -> None:
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client['support']
    
    def get_db(self):
        return self.client['support']
    
    def insert_into_db(self, file_name, audio_url):
        actual_fecha = datetime.now()
        fecha = actual_fecha.date()
        fecha = fecha.isoformat()
        calls_collection = self.db['calls']
        
        call_document = {
            'filename': file_name,
            'url': audio_url,
            'date': fecha,
            'estado': 'Pendiente'
        }
        calls_collection.insert_one(call_document)
    
    def get_all_calls(self):
        calls_collection = self.db['calls']
        return list(calls_collection.find())
    
    def get_all_detailed_results(self):
        detailed_result_collection = self.db['detailed_results']
        return list(detailed_result_collection.find())
    
    def get_all_summary_results(self):
        summary_result_collection = self.db['summary_results']
        return list(summary_result_collection.find())
    
    def serialize_object_ids(self, doc):
        if isinstance(doc, list):
            for item in doc:
                self.serialize_object_ids(item)
        elif isinstance(doc, dict):
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
                elif isinstance(value, (dict, list)):
                    self.serialize_object_ids(value)
        return doc