from django.urls import path
from .views import UniversityListAPIView

urlpatterns = [
    path('universities/', UniversityListAPIView.as_view(), name='university-list'),
]