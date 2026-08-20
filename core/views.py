from rest_framework import generics
from .models import University, Program, Application
from .serializers import UniversitySerializer, ProgramSerializer, ApplicationSerializer

# 1. University List View (Read Only)
class UniversityListAPIView(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer

# 2. Program List View (Read Only)
class ProgramListAPIView(generics.ListAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

# 3. Application CRUD Views (Create, Read)
class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    # ListCreateAPIView allows GET (List) and POST (Create)
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

# 4. Application Details Views (Read, Update, Delete)
class ApplicationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # RetrieveUpdateDestroyAPIView allows GET (Read one), PUT/PATCH (Update), and DELETE
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer