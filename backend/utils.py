from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
from datetime import datetime

#DB
def get_db():
    client = MongoClient('mongodb+srv://support:JPB2v7xa1rwGmjS8@cluster0.rxj5qey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['support']
    return db

def insert_into_db(file_name, audio_url):
    db = get_db()
    actual_fecha = datetime.now()
    fecha = actual_fecha.date()
    fecha = fecha.isoformat()
    calls_collection = db['calls']
    
    call_document = {
        'filename': file_name,
        'url': audio_url,
        'date': fecha,
        'estado': 'Pendiente'
    }
    calls_collection.insert_one(call_document)
    
def get_estimated_timecall():
    pass

#Serializar
class CallSerializer(serializers.Serializer):
    url = serializers.URLField()
    date = serializers.DateTimeField()

#View
@api_view(['POST'])
def add_call(request):
    serializer = CallSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        url = data['url']
        date = data['date']

        db = get_db()
        calls_collection = db['calls']
        
        call_document = {
            'url': url,
            'date': date
        }
        calls_collection.insert_one(call_document)

        return Response({'message': 'Call added successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


