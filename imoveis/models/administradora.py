from django.db import models
from utils.abstract_model import BaseModelTimeStamped, BaseModelEndereco


class Administradora(BaseModelTimeStamped):
    """
    Administradora é a empresa que gerencia os imóveis.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome")
    email = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="E-mail"
    )
    site = models.URLField(max_length=200, blank=True, null=True, verbose_name="Site")
    telefone = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Telefone"
    )

    class Meta:
        verbose_name = "Administradora"
        verbose_name_plural = "Administradoras"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
