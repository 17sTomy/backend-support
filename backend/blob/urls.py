from django.urls import path
from .views import AudioFileAPIView

urlpatterns = [
    path('audio/', AudioFileAPIView.as_view()),
]