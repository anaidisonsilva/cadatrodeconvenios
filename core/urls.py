"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("convenios/", include(("convenios.urls", "convenios"), namespace="convenios")),

    # suas apps
    path("convenios/", include("convenios.urls")),
    path("contratos/", include("contratos.urls")),
    path("financeiro/", include("financeiro.urls")),

    # relatorios (com namespace)
    path("relatorios/", include(("relatorios.urls", "relatorios"), namespace="relatorios")),

    # dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),
]

