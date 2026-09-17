"""web_fabi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from core import views as core_views
from django.conf import settings
from autocuidados import views as autocuidados_view
from nuevos_recursos import views as nuevos_recursos_view
from reservas import views as reservas_view
from actividades import views as actividades_view
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', core_views.panel, name='panel'),
    path('', core_views.inicio, name='inicio'),
    path('escuelaparaelbuentrato/', core_views.escuelaparaelbuentrato, name='escuelaparaelbuentrato'),
    path('contact/', core_views.contact, name='contact'),
    path('psicoterapia/', core_views.psicoterapia, name='psicoterapia'),
    path('autocuidado/', core_views.autocuidado, name='autocuidado'),
    path('recursosgratuitos/', nuevos_recursos_view.Nuevos_recursos, name='recursos'),
    path('recursosgratuitos/ansiedad/', nuevos_recursos_view.ansiedad, name='ansiedad'),
    path('recursosgratuitos/depresion/', nuevos_recursos_view.depresion, name='depresion'),
    path('galeria/<str:id_a>/', autocuidados_view.galeria_view, name='galeria_view'),
    path('reservar/', reservas_view.reservar, name='reservar'),
    path('actividades/', actividades_view.listado, name='actividades'),
    path('actividades/pasadas/', actividades_view.pasadas, name='actividades_pasadas'),
    path('actividades/<int:pk>/', actividades_view.detalle, name='actividad_detalle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)