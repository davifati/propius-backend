from django.contrib import admin
from imoveis.models import Condominio


@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ("nome", "administradora", "endereco", "get_unidades_count")
    list_filter = ("administradora",)
    search_fields = ("nome", "endereco", "email", "telefone")
    exclude = ("deletado_em",)

    def get_unidades_count(self, obj):
        return obj.unidades.count()

    get_unidades_count.short_description = "Número de Unidades"
