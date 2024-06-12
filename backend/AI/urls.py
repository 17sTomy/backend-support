# emotion_analysis/urls.py
from django.urls import path
from .views import EmotionAnalysisView, GenerateCSVView

urlpatterns = [
    path('analyze-emotions/', EmotionAnalysisView.as_view(), name='analyze-emotions'),
    path('csv', GenerateCSVView.as_view(), name='generate-csv'),
]
