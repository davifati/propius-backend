from rest_framework import serializers
from .falha import FalhaSerializer


class ImobiliariaSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    site = serializers.URLField()
    unidade = serializers.CharField(max_length=255)
    dadosFalhas = FalhaSerializer(many=True)
