from django.shortcuts import render

def contratos_home(request):
    return render(request, "contratos/home.html")
