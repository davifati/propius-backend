from rest_framework import serializers

from .administradora import AdministradoraSerializer
from .condominio import CondominioSerializer
from .unidade import UnidadeSerializer
from monitoramento.serializers.boleto import BoletoSerializer


class AtivoSerializer(serializers.Serializer):

    administradoras = AdministradoraSerializer(many=True)
    condominios = CondominioSerializer(many=True)
    unidades = UnidadeSerializer(many=True)


class AtivoImovelSerializer(serializers.Serializer):

    administradoras = AdministradoraSerializer(many=True)
    condominios = CondominioSerializer(many=True)
    unidades = UnidadeSerializer(many=True)
    boletos = BoletoSerializer(many=True)

    def to_representation(self, instance):
        boletos_valores = [boleto.valor for boleto in instance.boletos.all()][
            0
        ]  # TODO:
        return {
            "administradora": instance.condominio.administradora.nome,
            "administracao": instance.condominio.nome,
            "boleto": boletos_valores,
            "data_extracao_boletos": instance.criado_em.strftime("%d/%m/%Y"),
            "estado": "RJ",
            "status": "A Vencer",
        }
