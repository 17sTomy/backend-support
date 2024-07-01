# emotion_analysis/views.py
import os
import re
import subprocess
import json
import requests
import anthropic
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmotionAnalysisRequestSerializer,
)
from hume import HumeBatchClient
from hume.models.config import BurstConfig, ProsodyConfig
from collections import Counter
import datetime
from db import get_db
from rest_framework.decorators import api_view
from bson.json_util import dumps

class EmotionAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmotionAnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            if "youtu" in url:
                file = process_youtube_url(url)
                conversation_file_path = get_emotions(None, files=[file])
            else:
                conversation_file_path = get_emotions(url)    
            response_data = get_llm_response(conversation_file_path)
            output_data = ""
            for text_block in response_data:
                output_data += text_block.text + "\n"
        
            file_path = os.path.join(os.getcwd(), "output.txt")
            with open(file_path, "w") as f:
                f.write(output_data)
            
            print(f"Response saved to {file_path}")
            dateTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            json_file = extract_json_from_text(file_path, dateTime)
        

            db = get_db()
            people_collection = db['summary_results']
            people_collection.insert_one(json_file)

            return Response(output_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class GenerateCSVView(APIView):
    def post(self, request, *args, **kwargs):
        return Response("CSV generated", status=status.HTTP_200_OK)

@api_view(['GET'])
def get_summary_results(request):
    db = get_db()
    collection = db['summary_results']

    try:
        documents = list(collection.find())
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        
        return Response(documents, status=status.HTTP_200_OK, content_type='application/json')
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_emotions(url, files=None):
    client = HumeBatchClient(settings.HUME_API_KEY)
    prosody_config = ProsodyConfig(granularity="conversational_turn", identify_speakers=True)
    job = client.submit_job([url] if url else None, [prosody_config], files=files)
    job.await_complete()
    full_predictions = job.get_predictions()
    save_data_local(full_predictions, file_name="full_predictions.json")
    conversation = full_predictions[0]["results"]["predictions"][0]["models"]["prosody"]["grouped_predictions"]
    min_conversation = reduce_emotions(conversation)
    conversation_file_path = save_data_local(min_conversation, file_name="min_conversation.json")
    return conversation_file_path

def process_youtube_url(url):
    output_file_path = os.path.join(os.getcwd(), "audio_file.mp3")
    subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_file_path, url], check=True)
    return output_file_path
  
def extract_overall_emotions(predictions):
    output = []
    for prediction in predictions:
        prosody_emotions = []

        prosody_predictions = prediction["models"]["prosody"]["grouped_predictions"]
        for prosody_prediction in prosody_predictions:
            for segment in prosody_prediction["predictions"][:1]:
                prosody_emotions.append(segment["emotions"])
                
        output.append({
            "prosody_emotions": prosody_emotions,
        })
    return output
  
def save_data_local(data, file_name="data.json", file_path=os.getcwd()):
    full_path = file_path + "/" + file_name
    with open(full_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been written to {full_path}")
    return full_path
  
def get_llm_response(conversation_path):
    print("Getting LLM response")
    client = anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY,
    )
    
    with open(os.getcwd() + "/prompt.txt", "r") as f:
        prompt = f.read().strip()
    with open(conversation_path, "r") as f:
        json_data = f.read()
        
    input_data = prompt + "\n\n" + json_data
    print("Sending message to LLM")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": input_data}
        ]
    )
    print("Message received from LLM")
    return message.content

def reduce_emotions(data, emotions_count=5):
    output_data = []
    for entry in data:
        if 'predictions' in entry:
          for prediction in entry['predictions']:
              if 'emotions' in prediction:
                  prediction['emotions'] = sorted(prediction['emotions'], key=lambda x: x['score'], reverse=True)[:emotions_count]
        output_data.append(entry)
    return output_data

def extract_json_from_text(file_path, date):
    with open(file_path, 'r') as file:
        text = file.read()
    
    # Usar una expresión regular para encontrar el contenido JSON
    json_match = re.search(r'{.*}', text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        json_obj = json.loads(json_str)
        with open(f'jsons/output{date}.json', "w") as f:
            json.dump(json_obj, f, indent=4)    
        return json_obj
    else:
        return None