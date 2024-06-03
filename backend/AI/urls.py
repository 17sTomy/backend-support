# emotion_analysis/urls.py
from django.urls import path
from .views import EmotionAnalysisView

urlpatterns = [
    path('analyze-emotions/', EmotionAnalysisView.as_view(), name='analyze-emotions'),
]
