from datetime import date
from django.db import models
from django.conf import settings
from django.db.models import Sum


class Convenio(models.Model):
    class Tipo(models.TextChoices):
        FEDERAL = "FEDERAL", "Federal"
        ESTADUAL = "ESTADUAL", "Estadual"
        EMENDA_SAUDE = "EMENDA_SAUDE", "Emenda (Saúde)"
        ESPECIAL = "ESPECIAL", "Especial"

    class Status(models.TextChoices):
        CAPTACAO = "CAPTACAO", "Em captação"
        PROPOSTA = "PROPOSTA", "Proposta"
        CONVENIADO = "CONVENIADO", "Conveniado"
        EXECUCAO = "EXECUCAO", "Em execução"
        PRESTACAO = "PRESTACAO", "Prestação de contas"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    tipo = models.CharField(max_length=20, choices=Tipo.choices)

    numero_indicacao = models.CharField("Nº da Indicação/Emenda", max_length=60, blank=True, null=True)
    numero_proposta = models.CharField("Nº da Proposta", max_length=60, blank=True, null=True)
    numero_convenio = models.CharField("Nº do Convênio/Instrumento", max_length=60, blank=True, null=True)

    parlamentar_nome = models.CharField("Parlamentar", max_length=150, blank=True, null=True)
    orgao_concedente = models.CharField("Órgão concedente", max_length=200)
    objeto = models.TextField()

    valor_repasse = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valor_contrapartida = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    vigencia_inicio = models.DateField()
    vigencia_fim = models.DateField()

    # >>> NOVO: pago pelo órgão concedente
    repasse_recebido = models.BooleanField("Repasse recebido (Órgão já pagou?)", default=False)

    foi_licitado = models.BooleanField(default=False)
    modalidade = models.CharField(max_length=60, blank=True, null=True)
    numero_processo_licitatorio = models.CharField(max_length=80, blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSTA)
    observacoes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["vigencia_fim", "orgao_concedente"]

    def __str__(self):
        return f"{self.orgao_concedente} - {self.numero_convenio or self.numero_proposta or self.numero_indicacao or 'Sem número'}"

    @property
    def valor_total(self):
        return (self.valor_repasse or 0) + (self.valor_contrapartida or 0)

    @property
    def dias_para_vencer(self) -> int:
        return (self.vigencia_fim - date.today()).days

    @property
    def alerta_vigencia(self) -> str:
        d = self.dias_para_vencer
        if d < 0:
            return "VENCIDO"
        if d <= 30:
            return "VERMELHO"
        if d <= 90:
            return "AMARELO"
        return "OK"

    @property
    def total_pago(self):
        return self.contratos.aggregate(s=Sum("pagamentos__valor_pago"))["s"] or 0

    @property
    def total_contratado_atualizado(self):
        total = 0
        for c in self.contratos.all():
            total += c.valor_atualizado
        return total

    @property
    def saldo_financeiro(self):
        return self.valor_total - self.total_pago