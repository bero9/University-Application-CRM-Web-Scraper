from rest_framework import serializers
from .models import University, Program, Application

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    # Add a custom read-only field to show the university name instead of just its ID
    university_name = serializers.ReadOnlyField(source='university.name')

    class Meta:
        model = Program
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        # Security: Prevent users from manually modifying these fields
        read_only_fields = ['created_at', 'updated_at', 'user'] # We added 'user' here