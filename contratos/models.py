from django.db import models
from django.db.models import Sum


class Empresa(models.Model):
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=220)
    nome_fantasia = models.CharField(max_length=220, blank=True, null=True)

    class Meta:
        ordering = ["razao_social"]

    def __str__(self):
        return self.nome_fantasia or self.razao_social


class Contrato(models.Model):
    convenio = models.ForeignKey("convenios.Convenio", on_delete=models.CASCADE, related_name="contratos")
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="contratos")

    numero_contrato = models.CharField(max_length=80)
    numero_processo = models.CharField(max_length=80, blank=True, null=True)
    objeto_contratado = models.TextField()

    valor_contratado = models.DecimalField(max_digits=14, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)

    class Status(models.TextChoices):
        ATIVO = "ATIVO", "Ativo"
        ENCERRADO = "ENCERRADO", "Encerrado"
        RESCINDIDO = "RESCINDIDO", "Rescindido"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ATIVO)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.numero_contrato} - {self.empresa}"

    @property
    def total_pago(self):
        return self.pagamentos.aggregate(s=Sum("valor_pago"))["s"] or 0

    @property
    def acrescimos(self):
        return self.aditivos.aggregate(s=Sum("valor_acrescimo"))["s"] or 0

    @property
    def supressoes(self):
        return self.aditivos.aggregate(s=Sum("valor_supressao"))["s"] or 0

    @property
    def valor_atualizado(self):
        return (self.valor_contratado or 0) + self.acrescimos - self.supressoes

    @property
    def saldo(self):
        return self.valor_atualizado - self.total_pago


class Aditivo(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="aditivos")

    class Tipo(models.TextChoices):
        PRAZO = "PRAZO", "Prazo"
        VALOR = "VALOR", "Valor"
        QUANTITATIVO = "QUANTITATIVO", "Quantitativo"
        REAJUSTE = "REAJUSTE", "Reajuste"
        SUPRESSAO = "SUPRESSAO", "Supressão"

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    numero_aditivo = models.CharField(max_length=80)
    data = models.DateField()

    valor_acrescimo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valor_supressao = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    dias_prazo = models.IntegerField(default=0)

    justificativa = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.numero_aditivo} ({self.get_tipo_display()})"
