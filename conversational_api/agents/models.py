#agents/models.py
from django.db import models
from django.core.exceptions import ValidationError

class Agent(models.Model):
    name = models.CharField(max_length=255)
    bland_ai_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Allow null and blank initially
    prompt = models.TextField()
    script = models.TextField(blank=True, null=True)
    voice = models.CharField(max_length=100, default="default_voice")
    analysis_schema = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    pathway_id = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=10, default="ENG")
    webhook = models.URLField(null=True, blank=True)
    model = models.CharField(max_length=50, default="enhanced")
    first_sentence = models.TextField(null=True, blank=True)
    tools = models.JSONField(null=True, blank=True)
    dynamic_data = models.JSONField(null=True, blank=True)
    interruption_threshold = models.IntegerField(default=100)
    keywords = models.JSONField(null=True, blank=True)
    max_duration = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class ConversationalPathway(models.Model):
    # Name and description of the pathway
    name = models.CharField(max_length=255, default='default_name')
    description = models.TextField(null=True, blank=True)

    # Bland AI-specific fields(Agent)
    bland_ai_pathway_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Optional fields for storing the pathway's structure (nodes and edges)
    nodes = models.JSONField(null=True, blank=True)  # Stores nodes as a JSON structure
    edges = models.JSONField(null=True, blank=True)  # Stores edges as a JSON structure

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0)

    
    class Meta:
        ordering = ['created_at'] 

    def __str__(self):
        return self.name    