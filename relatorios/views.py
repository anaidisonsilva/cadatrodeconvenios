import base64
from io import BytesIO
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from decimal import Decimal
from datetime import datetime, time, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce, TruncMonth

from weasyprint import HTML
from convenios.models import Convenio


# =========================
# Helpers de gráfico (PDF)
# =========================

def _fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def chart_bar(labels, values, title):
    fig = plt.figure(figsize=(8, 3.2))
    ax = fig.add_subplot(111)
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel("Qtd")
    ax.tick_params(axis="x", rotation=15)
    return _fig_to_base64(fig)


def chart_pie(labels, values, title):
    fig = plt.figure(figsize=(7, 3.2))
    ax = fig.add_subplot(111)
    if sum(values) == 0:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
    else:
        ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
    ax.set_title(title)
    return _fig_to_base64(fig)


def chart_line(labels, values, title):
    fig = plt.figure(figsize=(8, 3.2))
    ax = fig.add_subplot(111)
    ax.plot(labels, values, marker="o")
    ax.set_title(title)
    ax.set_ylabel("R$")
    ax.tick_params(axis="x", rotation=25)
    return _fig_to_base64(fig)


# =========================
# Views
# =========================

def relatorios_home(request):
    return render(request, "relatorios/home.html")


def _apply_filters(request, qs):
    """
    Aplica filtros do GET no queryset de convênios.
    Compatível com DateField ou DateTimeField.
    Suporta filtro especial de "status":
      - OK / Vencendo / Vencidos  -> baseado em vigencia_fim
    E filtro por:
      - repasse_recebido (1/0)
      - parlamentar (texto)
    """
    data_ini = parse_date((request.GET.get("data_ini") or "").strip())
    data_fim = parse_date((request.GET.get("data_fim") or "").strip())

    status = (request.GET.get("status") or "").strip()
    orgao = (request.GET.get("orgao") or "").strip()  # input name="orgao"
    tipo = (request.GET.get("tipo") or "").strip()
    modalidade = (request.GET.get("modalidade") or "").strip()

    # ✅ parlamentar (input name="parlamentar")
    parlamentar = (request.GET.get("parlamentar") or "").strip()

    # ✅ repasse_recebido (select name="repasse_recebido")
    repasse_recebido = (request.GET.get("repasse_recebido") or "").strip()

    ini_is_dt = Convenio._meta.get_field("vigencia_inicio").get_internal_type() == "DateTimeField"
    fim_is_dt = Convenio._meta.get_field("vigencia_fim").get_internal_type() == "DateTimeField"

    # Datas (mantendo NULL também)
    if data_ini:
        if ini_is_dt:
            dt_ini = timezone.make_aware(datetime.combine(data_ini, time.min))
            qs = qs.filter(Q(vigencia_inicio__isnull=True) | Q(vigencia_inicio__gte=dt_ini))
        else:
            qs = qs.filter(Q(vigencia_inicio__isnull=True) | Q(vigencia_inicio__gte=data_ini))

    if data_fim:
        if fim_is_dt:
            dt_fim = timezone.make_aware(datetime.combine(data_fim, time.max))
            qs = qs.filter(Q(vigencia_fim__isnull=True) | Q(vigencia_fim__lte=dt_fim))
        else:
            qs = qs.filter(Q(vigencia_fim__isnull=True) | Q(vigencia_fim__lte=data_fim))

    # Status especial ou status do banco
    if status:
        hoje = timezone.localdate()
        st = status.upper()
        if st == "VENCIDOS":
            qs = qs.filter(vigencia_fim__lt=hoje)
        elif st == "VENCENDO":
            qs = qs.filter(vigencia_fim__gte=hoje, vigencia_fim__lte=hoje + timedelta(days=30))
        elif st == "OK":
            qs = qs.filter(vigencia_fim__gt=hoje + timedelta(days=30))
        else:
            qs = qs.filter(status__iexact=status)

    if orgao:
        qs = qs.filter(orgao_concedente__icontains=orgao)

    if tipo:
        qs = qs.filter(tipo__icontains=tipo)

    if modalidade:
        qs = qs.filter(modalidade__icontains=modalidade)

    if parlamentar:
        qs = qs.filter(parlamentar_nome__icontains=parlamentar)

    if repasse_recebido == "1":
        qs = qs.filter(repasse_recebido=True)
    elif repasse_recebido == "0":
        qs = qs.filter(repasse_recebido=False)

    return qs.distinct()


def relatorios_dados(request):
    """
    JSON para os gráficos (sempre com filtros aplicados).
    Retorna também totais para os cards:
      - total_repasse
      - total_contrapartida
      - total_geral
    E na lista retorna:
      - valor_contrapartida
      - parlamentar_nome
      - repasse_recebido
    """
    try:
        qs = _apply_filters(request, Convenio.objects.all())

        totais = qs.aggregate(
            total_repasse=Coalesce(Sum("valor_repasse"), Decimal("0")),
            total_contrapartida=Coalesce(Sum("valor_contrapartida"), Decimal("0")),
        )
        total_repasse = totais["total_repasse"] or Decimal("0")
        total_contra = totais["total_contrapartida"] or Decimal("0")

        por_tipo = list(
            qs.values("tipo")
              .annotate(qtd=Count("id", distinct=True))
              .order_by("tipo")
        )
        for i in por_tipo:
            i["tipo"] = i["tipo"] or "Não informado"

        por_status = list(
            qs.values("status")
              .annotate(qtd=Count("id", distinct=True))
              .order_by("status")
        )
        for i in por_status:
            i["status"] = i["status"] or "Não informado"

        repasse_por_mes = list(
            qs.exclude(vigencia_inicio__isnull=True)
              .annotate(mes=TruncMonth("vigencia_inicio"))
              .values("mes")
              .annotate(repasse=Coalesce(Sum("valor_repasse"), Decimal("0")))
              .order_by("mes")
        )
        repasse_por_mes_fmt = [
            {"mes": r["mes"].strftime("%Y-%m"), "repasse": float(r["repasse"])}
            for r in repasse_por_mes
        ]

        lista = list(
            qs.order_by("-vigencia_fim")
              .values(
                  "id",
                  "numero_convenio",
                  "orgao_concedente",
                  "parlamentar_nome",
                  "tipo",
                  "status",
                  "repasse_recebido",
                  "valor_repasse",
                  "valor_contrapartida",
                  "vigencia_inicio",
                  "vigencia_fim",
              )[:200]
        )

        return JsonResponse({
            "ok": True,
            "qtd_total": qs.count(),
            "total_repasse": float(total_repasse),
            "total_contrapartida": float(total_contra),
            "total_geral": float(total_repasse + total_contra),
            "por_tipo": por_tipo,
            "por_status": por_status,
            "repasse_por_mes": repasse_por_mes_fmt,
            "lista": lista,
        })

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def relatorio_pdf(request):
    qs = _apply_filters(request, Convenio.objects.all().order_by("-vigencia_fim"))

    def pick(obj, *fields, default="-"):
        for f in fields:
            if hasattr(obj, f):
                v = getattr(obj, f)
                if v not in (None, ""):
                    return v
        return default

    def to_decimal(v):
        if v in (None, ""):
            return Decimal("0")
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except Exception:
            return Decimal("0")

    rows = []
    for c in qs:
        repasse = to_decimal(pick(c, "valor_repasse", default=0))
        contrapartida = to_decimal(pick(c, "valor_contrapartida", default=0))
        rows.append({
            "numero": pick(c, "numero_convenio", default="-"),
            "objeto": pick(c, "objeto", default="-"),
            "orgao": pick(c, "orgao_concedente", default="-"),
            "parlamentar": pick(c, "parlamentar_nome", default="-"),
            "tipo": pick(c, "tipo", default="-"),
            "status": pick(c, "status", default="-"),
            "repasse_recebido": "Sim" if getattr(c, "repasse_recebido", False) else "Não",
            "inicio": pick(c, "vigencia_inicio", default=None),
            "fim": pick(c, "vigencia_fim", default=None),
            "repasse": repasse,
            "contrapartida": contrapartida,
            "total": repasse + contrapartida,
        })

    totais = qs.aggregate(
        total_repasse=Coalesce(Sum("valor_repasse"), Decimal("0")),
        total_contrapartida=Coalesce(Sum("valor_contrapartida"), Decimal("0")),
    )
    total_repasse = totais["total_repasse"] or Decimal("0")
    total_contra = totais["total_contrapartida"] or Decimal("0")

    # =========================
    # ✅ GRÁFICOS PARA O PDF
    # =========================

    por_tipo = list(
        qs.values("tipo")
          .annotate(qtd=Count("id", distinct=True))
          .order_by("tipo")
    )
    labels_tipo = [(i["tipo"] or "Não informado") for i in por_tipo]
    values_tipo = [int(i["qtd"]) for i in por_tipo]
    grafico_tipo = chart_bar(labels_tipo, values_tipo, "Convênios por Tipo")

    por_status = list(
        qs.values("status")
          .annotate(qtd=Count("id", distinct=True))
          .order_by("status")
    )
    labels_status = [(i["status"] or "Não informado") for i in por_status]
    values_status = [int(i["qtd"]) for i in por_status]
    grafico_status = chart_pie(labels_status, values_status, "Convênios por Status")

    repasse_por_mes = list(
        qs.exclude(vigencia_inicio__isnull=True)
          .annotate(mes=TruncMonth("vigencia_inicio"))
          .values("mes")
          .annotate(repasse=Coalesce(Sum("valor_repasse"), Decimal("0")))
          .order_by("mes")
    )
    labels_mes = [r["mes"].strftime("%Y-%m") for r in repasse_por_mes]
    values_mes = [float(r["repasse"]) for r in repasse_por_mes]
    grafico_mes = chart_line(labels_mes, values_mes, "Repasse por mês")

    context = {
        "titulo": "Relatório Geral de Convênios",
        "rows": rows,
        "qtd_convenios": qs.count(),
        "total_repasse": total_repasse,
        "total_contrapartida": total_contra,
        "total_geral": total_repasse + total_contra,
        "gerado_em": timezone.now(),
        "filtros": request.GET.dict(),

        # ✅ gráficos como imagem (base64)
        "grafico_tipo": grafico_tipo,
        "grafico_status": grafico_status,
        "grafico_mes": grafico_mes,
    }

    html_string = render_to_string("relatorios/pdf.html", context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="relatorio_convenios.pdf"'
    return response
