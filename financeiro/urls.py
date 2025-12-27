from django.urls import path
from . import views

app_name = "financeiro"

urlpatterns = [
    # ajuste para a sua view real (exemplo)
    path("", views.financeiro_home, name="home"),
]
