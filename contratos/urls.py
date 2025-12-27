from django.urls import path
from . import views

app_name = "contratos"

urlpatterns = [
    # ajuste para sua view real (exemplo)
    path("", views.contratos_home, name="home"),
]
