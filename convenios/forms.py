from django import forms
from .models import Convenio

class ConvenioForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = [
            "tipo",
            "numero_indicacao",
            "numero_proposta",
            "numero_convenio",
            "parlamentar_nome",
            "orgao_concedente",
            "objeto",
            "valor_repasse",
            "valor_contrapartida",
            "vigencia_inicio",
            "vigencia_fim",

            # ✅ novo
            "repasse_recebido",

            "foi_licitado",
            "modalidade",
            "numero_processo_licitatorio",
            "status",
            "observacoes",
        ]
        widgets = {
            "vigencia_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "vigencia_fim": forms.DateInput(attrs={"type": "date", "class": "form-control"}),

            # ✅ checkbox com bootstrap
            "repasse_recebido": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
