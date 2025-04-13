from django.contrib import admin
from imoveis.models import Administradora


@admin.register(Administradora)
class AdministradoraAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "get_condominios_count")
    search_fields = ("nome", "email", "telefone")
    exclude = ("deletado_em",)

    def get_condominios_count(self, obj):
        return obj.condominios.count()

    get_condominios_count.short_description = "Número de Condomínios"
