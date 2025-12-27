from django.db import models


class Pagamento(models.Model):
    contrato = models.ForeignKey("contratos.Contrato", on_delete=models.CASCADE, related_name="pagamentos")
    data = models.DateField()
    valor_pago = models.DecimalField(max_digits=14, decimal_places=2)

    numero_empenho = models.CharField(max_length=80, blank=True, null=True)
    numero_ob = models.CharField("Nº Ordem Bancária", max_length=80, blank=True, null=True)
    numero_nf = models.CharField("Nº Nota Fiscal", max_length=80, blank=True, null=True)

    observacao = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.contrato.numero_contrato} - {self.data} - R$ {self.valor_pago}"
