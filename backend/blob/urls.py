from django.urls import path
from .views import AudioFileAPIView
from .views import get_all_calls, get_all_detailed_results, get_all_summary_results, get_detailed_results_by_id, get_summary_results_by_id

urlpatterns = [
    path('audio/', AudioFileAPIView.as_view()),
    path("get-all-calls/" , get_all_calls, name="get_all_calls"),
    path("get-all-detailed-results/", get_all_detailed_results, name="get_all_detailed_results"),
    path("get-all-summary-results/", get_all_summary_results, name="get_summary_results"),
    path("summary-results-by-id/<str:id>/", get_summary_results_by_id, name="get_summary_results_by_id"),
    path("detailed-results-by-id/<str:id>/", get_detailed_results_by_id,  name="get_detailed_results_by_id")
]