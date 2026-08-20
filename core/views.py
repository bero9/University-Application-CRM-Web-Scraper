from rest_framework import generics
from .models import University, Program, Application
from .serializers import UniversitySerializer, ProgramSerializer, ApplicationSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import University, Program, Application, Document
from .serializers import UniversitySerializer, ProgramSerializer, ApplicationSerializer, DocumentSerializer
# 1. University List View (Read Only)
class UniversityListAPIView(generics.ListAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer

# 2. Program List View (Read Only)
class ProgramListAPIView(generics.ListAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

# 3. Application CRUD Views (Create, Read)# ... (Keep the imports and University/Program views as they are) ...

from rest_framework import permissions # Add this import at the top

# 3. Create and Read View for Applications
class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Override get_queryset to return ONLY applications owned by the logged-in user
    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    # Override perform_create to automatically attach the logged-in user to the application
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 4. Read, Update, and Delete View for a specific Application
class ApplicationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Override get_queryset to ensure users can only access their own applications
    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

# 5. Create and Read View for Documents (File Uploads)
class DocumentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Required to parse file uploads (form-data)
    parser_classes = [MultiPartParser, FormParser]

    # Only show documents for applications owned by the logged-in user
    def get_queryset(self):
        return Document.objects.filter(application__user=self.request.user)