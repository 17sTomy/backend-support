# emotion_analysis/urls.py
from django.urls import path
from .views import EmotionAnalysisView, GenerateCSVView, EmotionAnalysisWithAPI

urlpatterns = [
    path('analyze-emotions', EmotionAnalysisView.as_view(), name='analyze-emotions'),
    path('csv', GenerateCSVView.as_view(), name='generate-csv'),
    path('analyze-emotions-with-api', EmotionAnalysisWithAPI.as_view(), name='analyze-emotions-with-api')
]
