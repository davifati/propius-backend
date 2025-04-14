# serializers.py
from rest_framework import serializers
from monitoramento.models import Boleto
from imoveis.models import Unidade


class BoletoRemessaSerializer(serializers.ModelSerializer):
    condominio = serializers.SerializerMethodField()
    bloco = serializers.SerializerMethodField()
    unidade = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    valor = serializers.SerializerMethodField()
    data_vencimento = serializers.SerializerMethodField()
    linha_digitavel = serializers.CharField()
    link_pdf = serializers.URLField()
    administradora = serializers.SerializerMethodField()

    class Meta:
        model = Boleto
        fields = [
            "id",
            "administradora",
            "condominio",
            "unidade",
            "bloco",
            "nome",
            "valor",
            "data_vencimento",
            "linha_digitavel",
            "link_pdf",
        ]

    def get_unidade_obj(self, obj):
        return (
            Unidade.objects.filter(pasta=str(obj.pasta))
            .select_related("condominio__administradora")
            .first()
        )

    def get_condominio(self, obj):
        unidade = self.get_unidade_obj(obj)
        return (
            unidade.condominio.nome.upper() if unidade and unidade.condominio else "---"
        )

    def get_administradora(self, obj):
        unidade = self.get_unidade_obj(obj)
        return (
            unidade.condominio.administradora.nome.upper()
            if unidade and unidade.condominio and unidade.condominio.administradora
            else "---"
        )

    def get_bloco(self, obj):
        unidade = self.get_unidade_obj(obj)
        return unidade.bloco if unidade else "---"

    def get_unidade(self, obj):
        unidade = self.get_unidade_obj(obj)
        return unidade.unidade if unidade else "---"

    def get_nome(self, obj):
        unidade = self.get_unidade_obj(obj)
        return (
            unidade.proprietario_nome.upper()
            if unidade and unidade.proprietario_nome
            else "---"
        )

    def get_valor(self, obj):
        return (
            f"R$ {obj.valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        )

    def get_data_vencimento(self, obj):
        return obj.data_vencimento.strftime("%d/%m/%Y")
