from django.db import models
from django.utils import timezone
from django.utils.html import format_html



# Create your models here.
class autocuidados(models.Model):
    id_a = models.CharField(primary_key=True,max_length=10, verbose_name="ID autocuidado",default="0")
    clienteA = models.CharField(max_length=80,verbose_name="cliente autocuidado",default="sin asignar")
    image = models.ImageField(upload_to="projects")
    desA = models.TextField(verbose_name="Descripcion")
    lugarA = models.CharField(max_length=20,verbose_name="Lugar autocuidado",default="sin asignar")
    fechaA = models.DateField(default=timezone.now)  # Para un campo solo de fecha    
    
    def formatted_desA(self):
        # Usa linebreaks para que los saltos de línea se reflejen
        return format_html(self.desA.replace('\n', '<br>'))

    formatted_desA.allow_tags = True
    formatted_desA.short_description = 'Descripción con Saltos de Línea'

    class Meta:
        verbose_name="autocuidado"
        verbose_name_plural="autocuidados"

    def __str__(self):
        return f"Id autocuidado= {self.id_a}-Nombre cliente= {self.clienteA}"

class galeria(models.Model):
    image = models.ImageField(upload_to="autocuidados")
    autocuidado = models.ForeignKey(
        autocuidados,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name="autocuidado"
    )
    class Meta:
        verbose_name="imagen"
        verbose_name_plural="imagenes"

    def __str__(self):
        return f"autocuidado cliente={self.autocuidado.clienteA}"

