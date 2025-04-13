from rest_framework import serializers
from imoveis.models import Condominio


class CondominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condominio
        exclude = ["deletado_em"]  # Exclui o campo 'deletado_em'
