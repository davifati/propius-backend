from datetime import timezone
from django.db import models
from django_countries.fields import CountryField


class BaseModelTimeStamped(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    deletado_em = models.DateTimeField(
        blank=True, null=True, verbose_name="Deletado em"
    )

    class Meta:
        abstract = True  # Evita que essa tabela seja criada no banco

    def delete(self, *args, **kwargs):
        """Soft delete: marca como deletado sem remover do banco."""
        self.deletado_em = timezone.now()
        self.save()

    def restore(self):
        """Restaura um registro deletado."""
        self.deletado_em = None
        self.save()

    @property
    def is_deleted(self):
        """Retorna se o registro está deletado."""
        return self.deletado_em is not None


class BasePessoa(BaseModelTimeStamped):

    nome = models.CharField(max_length=150, verbose_name="Nome")
    cpf = models.CharField(max_length=25, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=25, unique=True, verbose_name="RG")
    telefone = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Telefone"
    )
    email = models.EmailField(
        max_length=200, unique=True, verbose_name="E-mail", blank=True, null=True
    )
    endereco = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Estado"
    )
    pais = CountryField(
        default="BR", blank=True, null=True, verbose_name="País"
    )  # Validação de país

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome


class BaseModelEndereco(models.Model):
    logradouro = models.CharField(max_length=200, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, verbose_name="Número")
    complemento = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Complemento"
    )
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    cep = models.CharField(max_length=9, verbose_name="CEP")

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        ordering = ["estado", "cidade", "bairro", "logradouro"]

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.complemento} - {self.bairro} - {self.cidade} - {self.estado} - {self.cep}"


class BaseTelefone(models.Model):
    numero = models.CharField(max_length=20, verbose_name="Número do Telefone")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ("celular", "Celular"),
            ("whatsapp", "WhatsApp"),
        ],
        default="comercial",
        verbose_name="Tipo",
    )

    class Meta:
        abstract = True
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"
