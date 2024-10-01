from django.db import models

class Agent(models.Model):
    name = models.CharField(max_length=255)    # name: Name of the agent.
    bland_ai_id = models.CharField(max_length=255, unique=True) # bland_ai_id: Unique identifier connected to Bland AI.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    html_input = models.TextField() # html_input: Raw HTML input from the agent.
    script = models.TextField(blank=True, null=True) # script: Normalized script converted from HTML input.

    def __str__(self):
        return self.name
    
class ConversationalPathway(models.Model):
    agent = models.ForeignKey(Agent, related_name='pathways', on_delete=models.CASCADE)
    content = models.TextField()
    sequence = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return f"Pathway {self.sequence} for {self.agent.name}"