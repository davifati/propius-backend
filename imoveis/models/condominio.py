from django.db import models
from utils.abstract_model import BaseModelTimeStamped
from .administradora import Administradora


class Condominio(BaseModelTimeStamped):

    # Add the proper ForeignKey relationship
    administradora = models.ForeignKey(
        Administradora,
        on_delete=models.CASCADE,
        related_name="condominios",
        verbose_name="Administradora da qual o condomínio faz parte",
        help_text="Refere-se à administradora responsável por esse condomínio.",
    )

    nome = models.CharField(max_length=200, verbose_name="Nome do Condomínio")
    endereco = models.CharField(max_length=200, verbose_name="Endereço")

    numero = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Número do Imóvel"
    )
    cep = models.CharField(max_length=20, verbose_name="CEP")
    email = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="E-mail"
    )
    telefone = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Telefone"
    )

    class Meta:
        verbose_name = "Condomínio"
        verbose_name_plural = "Condomínios"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
