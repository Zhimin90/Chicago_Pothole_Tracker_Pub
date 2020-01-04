from rest_framework import serializers

from world.models import WorldBorder, T_Potholes, Density_Map

#Serializer
class T_PotholesSerializer(serializers.ModelSerializer):
    class Meta:
        model = T_Potholes
        fields = '__all__'
