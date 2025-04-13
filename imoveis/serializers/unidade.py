from rest_framework import serializers
from imoveis.models import Unidade


class UnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        exclude = ["deletado_em"]
