from django.core.cache import cache


def _ip_cliente(request):
    adelante = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if adelante:
        return adelante.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "desconocida")


def demasiados_intentos(request, clave, limite=5, ventana_segundos=600):
    """
    Limita envíos por IP en una ventana de tiempo, usando el cache de Django.

    Sin CAPTCHA (no hay credencial de reCAPTCHA/hCaptcha configurada, mismo
    bloqueo que las notificaciones por email), esto es la defensa real
    contra floods de envíos automatizados en los formularios públicos.

    Ojo: usa el cache por defecto de Django (en memoria, por proceso) si no
    se configuró uno explícito en settings.py — alcanza para el volumen
    actual del sitio, pero si el despliegue de producción corre varios
    workers/procesos, cada uno cuenta por separado y el límite real
    efectivo es limite × cantidad de workers. Revisar si se mueve a un
    cache compartido (ej. Redis) antes de esa Fase 4.
    """
    clave_cache = f"ratelimit:{clave}:{_ip_cliente(request)}"
    intentos = cache.get(clave_cache, 0)
    if intentos >= limite:
        return True
    cache.set(clave_cache, intentos + 1, ventana_segundos)
    return False
