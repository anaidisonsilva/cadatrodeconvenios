from django.shortcuts import render

def financeiro_home(request):
    return render(request, "financeiro/home.html")