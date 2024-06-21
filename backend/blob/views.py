from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.azureUpdate import AzureBlobUploader

class AudioFileAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        account_name = 'suportplus'
        account_key = '5ZcfhelbpOBLQcKWS3DRdg9pqZXzCR7s/4axJQ8Kkufu6TMJI6Gdqt8lSDvWEP6B5dW1o0D9Apj7+AStJ3i46Q=='
        container_name = 'user'

        self.azure_blob_uploader = AzureBlobUploader(account_name, account_key, container_name)

    def post(self, request, *args, **kwargs):        
        for _, file in request.FILES.items():
            file_name = file.name
            if not file_name.endswith(('.mp3', '.wav')):
                return Response({"error": "Invalid file type. Only .mp3 and .wav are allowed."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                self.azure_blob_uploader.upload_file(file, file_name)
                pass
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": f"Archivo {file_name} subido exitosamente."}, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        file_name = request.query_params.get('file_name')

        if not file_name:
            return Response({'error': 'file_name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            audio_url = self.azure_blob_uploader.generate_file_url(file_name)
            return Response({'audio_url': audio_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)