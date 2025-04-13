from django.contrib import admin
from .models import Boleto


from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponseRedirect


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):


    exclude = ("deletado_em",)
