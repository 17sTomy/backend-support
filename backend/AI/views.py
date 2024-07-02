from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmotionAnalysisRequestSerializer,
)
from db import get_db
from rest_framework.decorators import api_view
from utils import run_ai
from django.views.decorators.csrf import csrf_exempt


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
    
@csrf_exempt
@api_view(["DELETE"])
def delete_summary_result(request):
    db = get_db()
    collection = db["summary_results"]
    

    summary_id = request.data.get("_id")
    
    if not summary_id:
        return Response({"error": "Missing '_id' in request data"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = collection.delete_one({"_id": summary_id})
        if result.deleted_count == 1:
            return Response("Deleted", status=status.HTTP_200_OK)
        else:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)