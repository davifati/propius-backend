from django.contrib import admin
from .models import Boleto


from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponseRedirect


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    # fields = ("origem", "data_vencimento", "status")
    # list_display = fields
    # list_filter = fields
    # search_fields = fields

    exclude = ("deletado_em",)
