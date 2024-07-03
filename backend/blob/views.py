from bson import ObjectId
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blob.azureUpdate import AzureBlobUploader
from dotenv import load_dotenv
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
import blob.mongoResourceDB as mongoResourceDB
import os
import logging
from rest_framework.decorators import api_view

# Configurar el logger
logger = logging.getLogger(__name__)

MONGODB = mongoResourceDB.MongoCommands()

class AudioFileAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        self.account_name = os.getenv("ACCOUNT_NAME")
        self.account_key = os.getenv("ACCOUNT_KEY")
        self.container_name = os.getenv("CONTAINER_NAME")

        self.azure_blob_uploader = AzureBlobUploader(
            self.account_name, self.account_key, self.container_name
        )

    def post(self, request, *args, **kwargs):
        for _, file in request.FILES.items():
            file_name = file.name
            if not file_name.endswith((".mp3", ".wav")):
                return Response(
                    {"error": "Invalid file type. Only .mp3 and .wav are allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                self.azure_blob_uploader.upload_file(file, file_name)
                audio_url = self.azure_blob_uploader.generate_file_url(file_name)
                MONGODB.insert_into_db(file_name= file_name, audio_url= audio_url)
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                {"message": f"Archivo {file_name} subido exitosamente."},
                status=status.HTTP_201_CREATED,
            )


    def get(self, request):
        file_name = request.query_params.get("file_name")

        if not file_name:
            return Response(
                {"error": "file_name parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # audio_url = self.azure_blob_uploader.generate_file_url(file_name)
            audio_url = self.generate_file_url(file_name)
            return Response({"audio_url": audio_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_file_url(self, file_name):
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            container_name=self.container_name,
            blob_name=file_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}?{sas_token}"


@api_view(["GET"])    
def get_all_calls(request):
    db = MONGODB.get_db()
    collection = db["calls"]
    try:
        documents = list(collection.find())
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return Response(documents, status=200, content_type="application/json")
    except Exception as e:
        return Response({'error': 'No data found'}, status=404)

@api_view(["GET"])  
def get_all_detailed_results(request):
    db = MONGODB.get_db()
    collection = db["detailed_results"]
    try:
        documents = list(collection.find())
        return Response(documents, status=200, content_type="application/json")
    except Exception as e:
        return Response({'error': 'No data found'}, status=404)

@api_view(["GET"])  
def get_all_summary_results(request):
    db = MONGODB.get_db()
    collection = db['summary_results']
    try:
        documents = list(collection.find())
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            doc["call_id"] = str(doc["call_id"])
        return Response(documents, status=200, content_type="application/json")
    except Exception as e:
        return Response({'error': 'No data found'}, status=404)
    
@api_view(["GET"])
def get_detailed_results_by_id(request, id):
    db = MONGODB.get_db()
    collection = db["detailed_results"]

    try:
        object_id = ObjectId(id)
        document = collection.find_one({"call_id": object_id})

        if document:
            document["_id"] = str(document["_id"])
            document["call_id"] = str(document["call_id"])
            return Response(document, status=200, content_type="application/json")
        else:
            return Response({'error': 'No data found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(["GET"])  
def get_summary_results_by_id(request, id):
    db = MONGODB.get_db()
    collection = db["summary_results"]

    try:
        object_id = ObjectId(id)
        document = collection.find_one({"call_id": object_id})

        if document:
            document["_id"] = str(document["_id"])
            document["call_id"] = str(document["call_id"])
            return Response(document, status=200, content_type="application/json")
        else:
            return Response({'error': 'No data found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
