from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UpdateProfileAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('update-profile/<int:pk>/', UpdateProfileAPIView.as_view()),
]