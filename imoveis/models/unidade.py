from django.db import models
from utils.abstract_model import BaseModelTimeStamped
from .condominio import Condominio


class Unidade(BaseModelTimeStamped):

    # Add the proper ForeignKey relationship
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name="unidades",
        verbose_name="Condomínio da qual a unidade faz parte",
        help_text="Refere-se ao condomínio ao qual esta unidade pertence.",
        null=True,  # Make it nullable for migration
        blank=True,  # Make it blankable for migration
    )

    bloco = models.CharField(max_length=50, blank=True, null=True, verbose_name="Bloco")
    unidade = models.IntegerField(
        verbose_name="Número da Unidade", null=True, blank=True
    )
    cep = models.CharField(max_length=20, blank=True, null=True, verbose_name="CEP")
    pasta = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Número da Pasta",
    )

    proprietario_documento = models.CharField(
        max_length=14, blank=True, null=True, verbose_name="Documento do Proprietário"
    )

    proprietario_nome = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Nome do Proprietário"
    )

    login = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Login"
    )
    senha = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Senha"
    )

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"

    def __str__(self):
        if self.condominio:
            return f"Unidade {self.unidade} - {self.condominio.nome}"
        return f"Unidade {self.unidade}"
