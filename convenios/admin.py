from django.contrib import admin
from django.utils.html import format_html
from .models import Convenio


@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "numero_convenio",
        "numero_proposta",
        "numero_indicacao",
        "orgao_concedente",
        "parlamentar_nome",
        "vigencia_fim",
        "badge_vigencia",
        "status",
        "valor_repasse",
        "valor_contrapartida",
        "valor_total",
        "total_pago",
        "saldo_financeiro",
    )
    list_filter = ("tipo", "status", "foi_licitado", "orgao_concedente")
    search_fields = (
        "numero_convenio",
        "numero_proposta",
        "numero_indicacao",
        "orgao_concedente",
        "parlamentar_nome",
        "objeto",
    )
    readonly_fields = ("created_at", "updated_at")

    def badge_vigencia(self, obj: Convenio):
        d = obj.dias_para_vencer
        if d < 0:
            return format_html('<b style="color:#b00020">VENCIDO ({}d)</b>', d)
        if d <= 30:
            return format_html('<b style="color:#b00020">🔴 {} dias</b>', d)
        if d <= 90:
            return format_html('<b style="color:#9a6a00">🟡 {} dias</b>', d)
        return format_html('<span style="color:#0a7a0a">🟢 {} dias</span>', d)

    badge_vigencia.short_description = "Alerta Vigência"
