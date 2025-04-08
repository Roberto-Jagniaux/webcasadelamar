from django.db import models
from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Create your models here.
class nuevos_recursos(models.Model):
    nomM = models.CharField(max_length=80,verbose_name="Nombre de Material")
    image = models.ImageField(upload_to="projects",null=True,blank=True)
    url = models.URLField(blank=True, verbose_name="URL")  # Campo para la URL completa
    def formatted_desM(self):
        # Usa linebreaks para que los saltos de línea se reflejen
        return format_html(self.desM.replace('\n', '<br>'))

    formatted_desM.allow_tags = True
    formatted_desM.short_description = 'Descripción con Saltos de Línea'
    class Meta:
        verbose_name="nuevos_recurso"
        verbose_name_plural="nuevos_recursos"

    def __str__(self):
        return f"Nombre Material= {self.nomM}"



class archivos(models.Model):
    nomA = models.CharField(max_length=60,verbose_name="Nombre de Archivo")
    desA = models.TextField(verbose_name="Descripción Archivo")
    file_upload = models.FileField(upload_to="files",verbose_name="archivo")
    categoria = models.ForeignKey(
        nuevos_recursos,
        on_delete=models.CASCADE,
        related_name='archivo',
        verbose_name="categoria"
    )

    def formatted_desM(self):
        # Usa linebreaks para que los saltos de línea se reflejen
        return format_html(self.desM.replace('\n', '<br>'))

    formatted_desM.allow_tags = True
    formatted_desM.short_description = 'Descripción con Saltos de Línea'


    class Meta:
        verbose_name="Archivo"
        verbose_name_plural="Archivos"

    def __str__(self):
        return f"Nombre Material= {self.nomA}"