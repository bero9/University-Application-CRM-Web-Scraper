from django.urls import path
from .views import (
    UniversityListAPIView,
    ProgramListAPIView,
    ApplicationListCreateAPIView,
    ApplicationDetailAPIView
)

urlpatterns = [
    # Endpoint for Universities (Read Only)
    path('universities/', UniversityListAPIView.as_view(), name='university-list'),
    
    # Endpoint for Programs (Read Only)
    path('programs/', ProgramListAPIView.as_view(), name='program-list'),
    
    # Endpoint for Applications (List and Create)
    path('applications/', ApplicationListCreateAPIView.as_view(), name='application-list-create'),
    
    # Endpoint for a specific Application (Retrieve, Update, Delete)
    # <int:pk> is used to pass the Primary Key (ID) of the application in the URL
    path('applications/<int:pk>/', ApplicationDetailAPIView.as_view(), name='application-detail'),
]