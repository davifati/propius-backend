from django.contrib import admin
from imoveis.models import Unidade


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ("unidade", "condominio", "bloco", "proprietario_nome", "pasta")
    list_filter = ("condominio", "bloco")
    search_fields = ("unidade", "proprietario_nome", "proprietario_documento", "pasta")
    exclude = ("deletado_em",)

    def get_administradora(self, obj):
        return obj.condominio.administradora

    get_administradora.short_description = "Administradora"
