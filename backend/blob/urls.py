from django.urls import path
from .views import AudioFileAPIView, get_all_calls, get_all_detailed_results, get_all_summary_results

urlpatterns = [
    path('audio/', AudioFileAPIView.as_view()),
    path("get-all-calls" , get_all_calls, name="get_all_calls"),
    path("get-all-detailed_results", get_all_detailed_results, name="get_all_detailed_results"),
    path("summary-results", get_all_summary_results, name="get_summary_results"),
]