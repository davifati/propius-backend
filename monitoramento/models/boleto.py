from django.db import models
from imoveis.models import Unidade
from utils.abstract_model import BaseModelTimeStamped


class Boleto(BaseModelTimeStamped):

    # unidade = models.ForeignKey(
    #    Unidade,
    #    on_delete=models.CASCADE,
    #    related_name="boletos",  # Acesso aos boletos pela unidade
    #    verbose_name="Unidade",
    #    help_text="A unidade à qual o boleto pertence.",
    # )

    pasta = models.IntegerField(unique=True, verbose_name="Número da Pasta")

    data_vencimento = models.DateField(
        verbose_name="Data de Vencimento", help_text="Data de vencimento do boleto."
    )

    valor = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do boleto.",
    )

    linha_digitavel = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Linha Digitável",
        help_text="Linha digitável do boleto (única).",
    )

    origem = models.CharField(
        max_length=255,
        verbose_name="Origem",
        help_text="Origem do boleto.",
        default="",
    )

    link_pdf = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Link do PDF",
        help_text="Link para o PDF do boleto.",
    )

    status = models.CharField(
        max_length=10,
        choices=(
            ("vencido", "Vencido"),
            ("pago", "Pago"),
            ("cancelado", "Cancelado"),
            ("a vencer", "A Vencer"),
        ),
        default="vencido",
        verbose_name="Status",
    )

    endereco = models.CharField(
        max_length=255,
        verbose_name="Endereço",
        help_text="Endereço do boleto.",
        default="",
    )

    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"
        ordering = ["data_vencimento"]

    def __str__(self):
        valor_formatado = (
            f"{self.valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        )
        data_formatada = self.data_vencimento.strftime("%d/%m/%Y")
        return (
            f"Boleto do {self.origem.upper()}: R$ {valor_formatado} | {data_formatada}"
        )
