# emotion_analysis/urls.py
from django.urls import path
from .views import EmotionAnalysisView, GenerateCSVView, get_summary_results, delete_summary_result

urlpatterns = [
    path("analyze-emotions", EmotionAnalysisView.as_view(), name="analyze-emotions"),
    path("csv", GenerateCSVView.as_view(), name="generate-csv"),
    path("summary-results", get_summary_results, name="get_summary_results"),
    path("delete-summary-result", delete_summary_result, name="delete_summary_result"),
]
