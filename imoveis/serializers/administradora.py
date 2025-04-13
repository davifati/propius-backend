from rest_framework import serializers
from imoveis.models import Administradora


class AdministradoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administradora
        exclude = ["deletado_em"]
