from collections import OrderedDict
from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from convenios.models import Convenio


def _alerta_bucket(vigencia_fim) -> str:
    hoje = timezone.localdate()
    d = (vigencia_fim - hoje).days

    if d < 0:
        return "Vencido"
    if d <= 30:
        return "Vermelho (≤30d)"
    if d <= 90:
        return "Amarelo (≤90d)"
    return "OK (>90d)"


def _ultimos_12_meses_labels():
    # labels no formato "2025-01", "2025-02"... (últimos 12 meses)
    d = timezone.localdate().replace(day=1)
    labels = []
    for _ in range(12):
        labels.append(d.strftime("%Y-%m"))
        # volta para o 1º dia do mês anterior
        d = (d - timedelta(days=1)).replace(day=1)
    labels.reverse()
    return labels


def dashboard(request):
    # Cards
    total_convenios = Convenio.objects.count()
    total_repasse = Convenio.objects.aggregate(s=Sum("valor_repasse"))["s"] or 0
    total_contrapartida = Convenio.objects.aggregate(s=Sum("valor_contrapartida"))["s"] or 0

    hoje = timezone.localdate()
    vencendo_30 = Convenio.objects.filter(
        vigencia_fim__lte=hoje + timedelta(days=30),
        vigencia_fim__gte=hoje
    ).count()

    vencendo_90 = Convenio.objects.filter(
        vigencia_fim__lte=hoje + timedelta(days=90),
        vigencia_fim__gte=hoje
    ).count()

    vencidos = Convenio.objects.filter(vigencia_fim__lt=hoje).count()

    context = {
        "total_convenios": total_convenios,
        "total_repasse": total_repasse,
        "total_contrapartida": total_contrapartida,
        "vencendo_30": vencendo_30,
        "vencendo_90": vencendo_90,
        "vencidos": vencidos,
    }
    return render(request, "dashboard.html", context)


def dashboard_data(request):
    # 1) Convênios por tipo
    por_tipo_qs = (
        Convenio.objects.values("tipo")
        .annotate(qtd=Count("id"), repasse=Sum("valor_repasse"))
        .order_by("tipo")
    )
    por_tipo = [
        {"tipo": x["tipo"], "qtd": x["qtd"], "repasse": float(x["repasse"] or 0)}
        for x in por_tipo_qs
    ]

    # 2) Repasse por mês (últimos 12 meses) - otimizado com TruncMonth
    labels = _ultimos_12_meses_labels()
    repasse_por_mes = OrderedDict((lab, 0.0) for lab in labels)

    inicio = timezone.localdate().replace(day=1) - timedelta(days=365)

    repasse_qs = (
        Convenio.objects.filter(vigencia_inicio__gte=inicio)
        .annotate(mes=TruncMonth("vigencia_inicio"))
        .values("mes")
        .annotate(total=Sum("valor_repasse"))
        .order_by("mes")
    )

    for row in repasse_qs:
        mes = row["mes"].date() if hasattr(row["mes"], "date") else row["mes"]
        key = mes.strftime("%Y-%m")
        if key in repasse_por_mes:
            repasse_por_mes[key] = float(row["total"] or 0)

    # 3) Alertas (OK / amarelo / vermelho / vencido)
    buckets = OrderedDict([
        ("OK (>90d)", 0),
        ("Amarelo (≤90d)", 0),
        ("Vermelho (≤30d)", 0),
        ("Vencido", 0),
    ])

    for c in Convenio.objects.only("vigencia_fim"):
        buckets[_alerta_bucket(c.vigencia_fim)] += 1

    return JsonResponse({
        "por_tipo": por_tipo,
        "repasse_por_mes": {
            "labels": list(repasse_por_mes.keys()),
            "values": list(repasse_por_mes.values()),
        },
        "alertas": {
            "labels": list(buckets.keys()),
            "values": list(buckets.values()),
        }
    })
