from django.contrib import admin
from financeiro.models import RemessaBancaria, RemessaBancariaBoleto, Boleto


@admin.register(RemessaBancaria)
class RemessaBancariaAdmin(admin.ModelAdmin):
    list_display = ("administradora", "condominio", "data_envio", "status")
    list_filter = ("status", "administradora", "condominio")
    search_fields = ("administradora__nome", "condominio__nome")
    readonly_fields = (
        "data_envio",
        "data_processamento",
        "arquivo_remessa",
        "arquivo_retorno",
    )
    date_hierarchy = "criado_em"


@admin.register(RemessaBancariaBoleto)
class RemessaBancariaBoletoAdmin(admin.ModelAdmin):
    list_display = ("remessa", "boleto", "processado", "data_processamento")
    list_filter = ("processado",)
    search_fields = ("boleto__numero",)
    readonly_fields = ("processado", "data_processamento", "mensagem_erro")
