from django.db import models

class Agent(models.Model):
    name = models.CharField(max_length=255)
    bland_ai_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    prompt = models.TextField(default='')
    script = models.TextField(blank=True, null=True)
    voice = models.CharField(max_length=100, default="default_voice")
    analysis_schema = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    pathway_id = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=10, default="ENG")
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
    
    def __str__(self):
        return self.name

class ConversationalPathway(models.Model):
    agent = models.ForeignKey(Agent, related_name='pathways', on_delete=models.CASCADE)
    content = models.TextField()
    sequence = models.PositiveIntegerField()
    bland_ai_pathway_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"Pathway {self.sequence} for {self.agent.name}"