from django.contrib import admin
from .models import Producto, Transaccion


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio", "activo")
    list_filter = ("tipo", "activo")


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("id", "medio_pago", "monto", "estado", "creada_en")
    list_filter = ("medio_pago", "estado")
