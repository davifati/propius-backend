from django.db import models
from django.utils.translation import gettext_lazy as _

from monitoramento.models.boleto import Boleto
from imoveis.models.administradora import Administradora
from imoveis.models.condominio import Condominio
from utils.abstract_model import BaseModelTimeStamped


class RemessaBancaria(BaseModelTimeStamped):
    """
    Model representing a bank remittance (remessa bancária).
    A remittance is a batch of boletos that are sent to the bank for processing.
    """

    STATUS_CHOICES = (
        ("pendente", _("Pendente")),
        ("processando", _("Processando")),
        ("processado", _("Processado")),
        ("erro", _("Erro")),
    )

    administradora = models.ForeignKey(
        Administradora,
        on_delete=models.CASCADE,
        related_name="remessas_bancarias",
        verbose_name=_("Administradora"),
    )
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name="remessas_bancarias",
        verbose_name=_("Condomínio"),
    )
    data_envio = models.DateTimeField(_("Data de Envio"), null=True, blank=True)
    data_processamento = models.DateTimeField(
        _("Data de Processamento"), null=True, blank=True
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default="pendente"
    )
    arquivo_remessa = models.FileField(
        _("Arquivo de Remessa"), upload_to="remessas/", null=True, blank=True
    )
    arquivo_retorno = models.FileField(
        _("Arquivo de Retorno"), upload_to="retornos/", null=True, blank=True
    )
    mensagem_erro = models.TextField(_("Mensagem de Erro"), null=True, blank=True)

    class Meta:
        verbose_name = _("Remessa Bancária")
        verbose_name_plural = _("Remessas Bancárias")
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Remessa {self.id} - {self.condominio} - {self.get_status_display()}"


class RemessaBancariaBoleto(BaseModelTimeStamped):
    """
    Model representing the relationship between a remittance and its boletos.
    """

    remessa = models.ForeignKey(
        RemessaBancaria,
        on_delete=models.CASCADE,
        related_name="boletos",
        verbose_name=_("Remessa"),
    )
    boleto = models.ForeignKey(
        Boleto,
        on_delete=models.CASCADE,
        related_name="remessas",
        verbose_name=_("Boleto"),
    )
    processado = models.BooleanField(_("Processado"), default=False)
    data_processamento = models.DateTimeField(
        _("Data de Processamento"), null=True, blank=True
    )
    mensagem_erro = models.TextField(_("Mensagem de Erro"), null=True, blank=True)

    class Meta:
        verbose_name = _("Boleto da Remessa")
        verbose_name_plural = _("Boletos da Remessa")
        unique_together = ["remessa", "boleto"]
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Boleto {self.boleto.id} - Remessa {self.remessa.id}"
