from rest_framework import serializers
from imoveis.serializers.administradora import AdministradoraSerializer
from imoveis.serializers.condominio import CondominioSerializer
from imoveis.serializers.unidade import UnidadeSerializer


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Serializer para respostas paginadas
    """

    results = serializers.ListField()
    total_pages = serializers.IntegerField()
    current_page = serializers.IntegerField()
    total_items = serializers.IntegerField()


class AtivoImovelSerializer(serializers.Serializer):
    """
    Serializer para a resposta da API de informações de imóveis
    """

    administradoras = PaginatedResponseSerializer()
    condominios = PaginatedResponseSerializer()
    unidades = PaginatedResponseSerializer()

    class Meta:
        ref_name = "AtivoImovelResponse"
