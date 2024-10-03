# agents/urls.py

from rest_framework import routers
from .views import AgentViewSet, ConversationalPathwayViewSet

router = routers.DefaultRouter()
router.register(r'agents', AgentViewSet)
router.register(r'pathways', ConversationalPathwayViewSet)

urlpatterns = router.urls