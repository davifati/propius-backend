from rest_framework import serializers
from monitoramento.models import Boleto


class BoletoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Boleto
        exclude = ["deletado_em"]
