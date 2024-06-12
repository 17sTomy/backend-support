# emotion_analysis/views.py
import os
import subprocess
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmotionAnalysisRequestSerializer,
    EmotionAnalysisResponseSerializer,
)
from hume import HumeBatchClient
from hume.models.config import BurstConfig, ProsodyConfig
import time


class EmotionAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmotionAnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            if "youtu" in url:
                file = self.process_youtube_url(url)
                response_data = self.get_emotions(None, files=[file])
            else:
                response_data = self.get_emotions(url)
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_emotions(self, url, files=None):
        client = HumeBatchClient(settings.HUME_API_KEY)
        burst_config = BurstConfig()
        prosody_config = ProsodyConfig()
        job = client.submit_job([url] if url else None, [burst_config, prosody_config], files=files)
        job.await_complete()
        full_predictions = job.get_predictions()

        response_data = []
        for source in full_predictions:
            source_name = url if url else files[0]
            # source_name = source["source"]["url"]
            predictions = source["results"]["predictions"]
            output = self.extract_overall_emotions(predictions)
            response_data = {
                "source_name": source_name,
                "output": output,
            }
        return response_data

    def process_youtube_url(self, url):
        output_file = os.path.join(os.getcwd(), "audio_file.mp3")
        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_file, url], check=True)
        return output_file
      
    def extract_overall_emotions(self, predictions):
        output = []
        for prediction in predictions:
            prosody_emotions = []
            burst_emotions = []

            prosody_predictions = prediction["models"]["prosody"][
                "grouped_predictions"
            ]
            for prosody_prediction in prosody_predictions:
                for segment in prosody_prediction["predictions"][:1]:
                    prosody_emotions.append(segment["emotions"])

            burst_predictions = prediction["models"]["burst"][
                "grouped_predictions"
            ]
            for burst_prediction in burst_predictions:
                for segment in burst_prediction["predictions"][:1]:
                    burst_emotions.append(segment["emotions"])
            output.append({
                "prosody_emotions": prosody_emotions,
                "burst_emotions": burst_emotions,
            })
        return output
            