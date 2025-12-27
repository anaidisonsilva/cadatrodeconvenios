from django.urls import path
from . import views

app_name = "convenios"

urlpatterns = [
    path("", views.convenios_list, name="list"),
    path("novo/", views.convenio_create, name="novo"),
    path("<int:pk>/editar/", views.convenio_update, name="editar"),
    path("<int:pk>/apagar/", views.convenio_delete, name="apagar"),
    path("apagar-selecionados/", views.convenios_delete_selected, name="delete_selected"),
]
