from django.contrib import admin
from .models import Pagamento


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("data", "contrato", "valor_pago", "numero_empenho", "numero_nf", "numero_ob")
    list_filter = ("data",)
    search_fields = (
        "contrato__numero_contrato",
        "contrato__empresa__razao_social",
        "numero_empenho",
        "numero_nf",
        "numero_ob",
    )
