from rest_framework import serializers



class FalhaSerializer(serializers.Serializer):
    data = serializers.DateField()
    motivo = serializers.CharField(max_length=255)
