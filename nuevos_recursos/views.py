from django.shortcuts import render,get_object_or_404
from .models import nuevos_recursos as nuevos_recursosModel  # Cambia el alias del modelo
from .models import archivos as archivos_Model  # Cambia el alias del modelo

from django.core.paginator import Paginator

def Nuevos_recursos(request):
    nuevo_recurso = nuevos_recursosModel.objects.all()  # Usa el alias del modelo

    return render(request, "core/recursosgratuitos.html",{'nuevo_recurso': nuevo_recurso})

    

def ansiedad(request):
    categoria = get_object_or_404(nuevos_recursosModel, nomM__iexact='Ansiedad')
    ansiedadR = nuevos_recursosModel.objects.all()  # Usa el alias del modelo
    archivos_ansiedad = archivos_Model.objects.filter(categoria=categoria)

    
    return render(request, "core/recursosgratuitos/ansiedad.html", {'ansiedadR': ansiedadR,'archivos':archivos_ansiedad})


def depresion(request):
    # Obtener el objeto de la categoría 'depresión'
    categoria = get_object_or_404(nuevos_recursosModel, nomM__iexact='depresión')
    
    # Filtrar archivos por esta categoría
    archivos_depresion = archivos_Model.objects.filter(categoria=categoria)
    
    # Opcional: Obtener todos los recursos
    depresionR = nuevos_recursosModel.objects.all()

    return render(request, "core/recursosgratuitos/depresion.html", {
        'depresionR': depresionR,
        'archivos': archivos_depresion
    })