from django.contrib import admin
from .models import Empresa, Contrato, Aditivo


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj")
    search_fields = ("razao_social", "nome_fantasia", "cnpj")


class AditivoInline(admin.TabularInline):
    model = Aditivo
    extra = 0


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_contrato",
        "convenio",
        "empresa",
        "valor_contratado",
        "valor_atualizado",
        "total_pago",
        "saldo",
        "status",
    )
    list_filter = ("status", "empresa")
    search_fields = (
        "numero_contrato",
        "numero_processo",
        "empresa__razao_social",
        "convenio__numero_convenio",
        "convenio__numero_proposta",
        "convenio__numero_indicacao",
    )
    inlines = [AditivoInline]
