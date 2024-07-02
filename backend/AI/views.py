from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmotionAnalysisRequestSerializer,
)
from db import get_db
from rest_framework.decorators import api_view
from utils import run_ai


class EmotionAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmotionAnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            output_data = run_ai(url)
            return Response(output_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateCSVView(APIView):
    def post(self, request, *args, **kwargs):
        return Response("CSV generated", status=status.HTTP_200_OK)


@api_view(["GET"])
def get_summary_results(request):
    db = get_db()
    collection = db["summary_results"]

    try:
        documents = list(collection.find())
        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return Response(
            documents, status=status.HTTP_200_OK, content_type="application/json"
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
