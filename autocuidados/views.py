from django.shortcuts import render,get_object_or_404
from .models import autocuidados as autocuidados_a  # Cambia el alias del modelo
from .models import galeria as galeria_a 


def autocuidados(request):
    # Obtén todos los objetos del modelo usando el alias
    autocuidados_u = autocuidados_a.objects.all()  

    # Renderiza la plantilla y pasa el contexto con el nombre 'autocuidados_u'
    return render(request, "core/autocuidadoparaequipos.html", {'autocuidados_u': autocuidados_u})





#def galeria_view(request, id_a):
 #   autocuidado = get_object_or_404(autocuidados, id_a=id_a)
  #  galeria = autocuidado.imagenes.all()  # Gracias al related_name en la relación

   # return render(request, "core/galeria.html", {'galeria': galeria,'autocuidado':ID})

def galeria_view(request, id_a):
    # Recuperar el objeto autocuidados correspondiente
    autocuidado = get_object_or_404(autocuidados_a, id_a=id_a)
    
    # Obtener todas las imágenes relacionadas a este autocuidado
    imagenes = autocuidado.imagenes.all()  # Usa el related_name definido en el modelo

    # Pasar los datos al template
    context = {
        'autocuidado': autocuidado,
        'imagenes': imagenes
    }
    return render(request, 'core/galeria.html', context)
