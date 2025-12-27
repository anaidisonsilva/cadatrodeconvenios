from django.urls import path
from . import views

app_name = "relatorios"

urlpatterns = [
    path("", views.relatorios_home, name="relatorios_home"),          # /relatorios/
    path("dados/", views.relatorios_dados, name="relatorios_dados"),  # /relatorios/dados/
    path("pdf/", views.relatorio_pdf, name="relatorio_pdf"),          # /relatorios/pdf/
]
