from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Convenio
from .forms import ConvenioForm


def convenios_list(request):
    qs = Convenio.objects.all().order_by("-id")

    # (Opcional) se um dia você quiser filtrar na lista por pago/não pago via URL:
    # /convenios/?repasse_recebido=1  (pagos)
    # /convenios/?repasse_recebido=0  (não pagos)
    repasse_recebido = (request.GET.get("repasse_recebido") or "").strip()
    if repasse_recebido == "1":
        qs = qs.filter(repasse_recebido=True)
    elif repasse_recebido == "0":
        qs = qs.filter(repasse_recebido=False)

    return render(request, "convenios/lista.html", {"convenios": qs})


def convenio_create(request):
    if request.method == "POST":
        form = ConvenioForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            if request.user.is_authenticated:
                obj.created_by = request.user

            obj.save()
            return redirect("convenios:list")
    else:
        form = ConvenioForm()

    return render(request, "convenios/novo.html", {"form": form, "editando": False})


def convenio_update(request, pk):
    convenio = get_object_or_404(Convenio, pk=pk)

    # ✅ ISSO é o que garante que no editar a data e o checkbox apareçam preenchidos:
    if request.method == "POST":
        form = ConvenioForm(request.POST, instance=convenio)
        if form.is_valid():
            form.save()
            return redirect("convenios:list")
    else:
        form = ConvenioForm(instance=convenio)

    return render(
        request,
        "convenios/novo.html",
        {"form": form, "editando": True, "convenio": convenio},
    )


@require_POST
def convenio_delete(request, pk):
    convenio = get_object_or_404(Convenio, pk=pk)
    convenio.delete()
    return redirect("convenios:list")


@require_POST
def convenios_delete_selected(request):
    ids = request.POST.getlist("ids")
    if ids:
        Convenio.objects.filter(id__in=ids).delete()
    return redirect("convenios:list")
