from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
from django.conf import settings
import os
import re
import subprocess
import json
import anthropic
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from hume import HumeBatchClient
from hume.models.config import ProsodyConfig

from datetime import datetime, timedelta
from db import get_db
from rest_framework.decorators import api_view
from azure.storage.blob import generate_blob_sas, BlobSasPermissions


# DB
def get_db():
    client = MongoClient(settings.MONGODB_URL)
    db = client["support"]
    return db


def insert_into_db(file_name, audio_url):
    db = get_db()
    actual_fecha = datetime.now()
    fecha = actual_fecha.date()
    fecha = fecha.isoformat()
    calls_collection = db["calls"]

    call_document = {
        "filename": file_name,
        "url": audio_url,
        "date": fecha,
        "estado": "Pendiente",
    }
    calls_collection.insert_one(call_document)


def get_estimated_timecall():
    pass


# Serializar
class CallSerializer(serializers.Serializer):
    url = serializers.URLField()
    date = serializers.DateTimeField()


# View
@api_view(["POST"])
def add_call(request):
    serializer = CallSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        url = data["url"]
        date = data["date"]

        db = get_db()
        calls_collection = db["calls"]

        call_document = {"url": url, "date": date}
        calls_collection.insert_one(call_document)

        return Response(
            {"message": "Call added successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_emotions(url, files=None):
    client = HumeBatchClient(settings.HUME_API_KEY)
    prosody_config = ProsodyConfig(
        granularity="conversational_turn", identify_speakers=True
    )
    job = client.submit_job([url] if url else None, [prosody_config], files=files)
    job.await_complete()
    full_predictions = job.get_predictions()
    save_data_local(full_predictions, file_name="full_predictions.json")
    conversation = full_predictions[0]["results"]["predictions"][0]["models"][
        "prosody"
    ]["grouped_predictions"]
    min_conversation = reduce_emotions(conversation)
    conversation_file_path = save_data_local(
        min_conversation, file_name="min_conversation.json"
    )
    return conversation_file_path


def process_youtube_url(url):
    output_file_path = os.path.join(os.getcwd(), "audio_file.mp3")
    subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_file_path, url],
        check=True,
    )
    return output_file_path


def extract_overall_emotions(predictions):
    output = []
    for prediction in predictions:
        prosody_emotions = []

        prosody_predictions = prediction["models"]["prosody"]["grouped_predictions"]
        for prosody_prediction in prosody_predictions:
            for segment in prosody_prediction["predictions"][:1]:
                prosody_emotions.append(segment["emotions"])

        output.append(
            {
                "prosody_emotions": prosody_emotions,
            }
        )
    return output


def save_data_local(data, file_name="data.json", file_path=os.getcwd()):
    full_path = file_path + "/" + file_name
    with open(full_path, "w") as json_file:
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
        messages=[{"role": "user", "content": input_data}],
    )
    print("Message received from LLM")
    return message.content


def reduce_emotions(data, emotions_count=5):
    output_data = []
    for entry in data:
        if "predictions" in entry:
            for prediction in entry["predictions"]:
                if "emotions" in prediction:
                    prediction["emotions"] = sorted(
                        prediction["emotions"], key=lambda x: x["score"], reverse=True
                    )[:emotions_count]
        output_data.append(entry)
    return output_data


def extract_json_from_text(file_path, date):
    with open(file_path, "r") as file:
        text = file.read()

    # Usar una expresión regular para encontrar el contenido JSON
    json_match = re.search(r"{.*}", text, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)
        json_obj = json.loads(json_str)
        with open(f"jsons/output{date}.json", "w") as f:
            json.dump(json_obj, f, indent=4)
        return json_obj
    else:
        return None


def run_ai(url, calls_id=None):
    if "youtu" in url:
        file = process_youtube_url(url)
        conversation_file_path = get_emotions(None, files=[file])
    else:
        conversation_file_path = get_emotions(url)
    response_data = get_llm_response(conversation_file_path)
    output_data = ""
    for text_block in response_data:
        output_data += text_block.text + "\n"

    output_dir = os.path.join(os.getcwd(), "jsons")
    os.makedirs(output_dir, exist_ok=True)
    dateTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_path = os.path.join(output_dir, f"output_{dateTime}.txt")
    with open(file_path, "w") as f:
        f.write(output_data)

    print(f"Response saved to {file_path}")
    dateTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    json_file = extract_json_from_text(file_path, dateTime)
    if calls_id:
        json_file["call_id"] = calls_id
    db = get_db()
    people_collection = db["summary_results"]
    people_collection.insert_one(json_file)
    return output_data


def generate_file_url(account_name, account_key, container_name, file_name):
    sas_token = generate_blob_sas(
        account_name=account_name,
        account_key=account_key,
        container_name=container_name,
        blob_name=file_name,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1),
    )
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{file_name}?{sas_token}"
