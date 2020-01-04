from world.models import T_Potholes
from rest_framework import viewsets, permissions
from .serializers import  T_PotholesSerializer

#Viewset
class T_PotholesViewSet(viewsets.ModelViewSet):
    queryset = T_Potholes.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = T_PotholesSerializer