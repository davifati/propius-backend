from rest_framework import serializers
from financeiro.models import RemessaBancaria, RemessaBancariaBoleto, Boleto


class RemessaBancariaBoletoSerializer(serializers.ModelSerializer):
    """Serializer for RemessaBancariaBoleto model."""

    boleto_numero = serializers.CharField(source="boleto.numero", read_only=True)
    boleto_valor = serializers.DecimalField(
        source="boleto.valor", max_digits=10, decimal_places=2, read_only=True
    )
    boleto_vencimento = serializers.DateField(
        source="boleto.data_vencimento", read_only=True
    )
    boleto_status = serializers.CharField(source="boleto.status", read_only=True)

    class Meta:
        model = RemessaBancariaBoleto
        fields = [
            "id",
            "boleto",
            "boleto_numero",
            "boleto_valor",
            "boleto_vencimento",
            "boleto_status",
            "processado",
            "data_processamento",
            "mensagem_erro",
            "criado_em",
        ]
        read_only_fields = [
            "processado",
            "data_processamento",
            "mensagem_erro",
            "criado_em",
        ]


class RemessaBancariaSerializer(serializers.ModelSerializer):
    """Serializer for RemessaBancaria model."""

    boletos = RemessaBancariaBoletoSerializer(many=True, read_only=True)
    administradora_nome = serializers.CharField(
        source="administradora.nome", read_only=True
    )
    condominio_nome = serializers.CharField(source="condominio.nome", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = RemessaBancaria
        fields = [
            "id",
            "administradora",
            "administradora_nome",
            "condominio",
            "condominio_nome",
            "data_envio",
            "data_processamento",
            "status",
            "status_display",
            "arquivo_remessa",
            "arquivo_retorno",
            "mensagem_erro",
            "boletos",
            "criado_em",
        ]
        read_only_fields = [
            "data_envio",
            "data_processamento",
            "status",
            "arquivo_remessa",
            "arquivo_retorno",
            "mensagem_erro",
            "criado_em",
        ]


class RemessaBancariaCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new RemessaBancaria."""

    boletos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        help_text="List of boleto IDs to include in the remessa",
    )

    class Meta:
        model = RemessaBancaria
        fields = ["administradora", "condominio", "boletos_ids"]

    def validate_boletos_ids(self, value):
        """Validate that all boletos exist and belong to the specified condominio."""
        condominio_id = self.initial_data.get("condominio")
        if not condominio_id:
            raise serializers.ValidationError("Condomínio é obrigatório")

        boletos = Boleto.objects.filter(
            id__in=value, unidade__condominio_id=condominio_id
        )
        if len(boletos) != len(value):
            raise serializers.ValidationError(
                "Um ou mais boletos não foram encontrados ou não pertencem ao condomínio especificado"
            )

        return value

    def create(self, validated_data):
        """Create a new RemessaBancaria with its associated boletos."""
        boletos_ids = validated_data.pop("boletos_ids")
        remessa = super().create(validated_data)

        # Create RemessaBancariaBoleto instances
        RemessaBancariaBoleto.objects.bulk_create(
            [
                RemessaBancariaBoleto(remessa=remessa, boleto_id=boleto_id)
                for boleto_id in boletos_ids
            ]
        )

        return remessa
