from django.core.exceptions import ValidationError

LIMITE_IMAGEN_MB = 5
LIMITE_PDF_MB = 10


def validar_tamano_imagen(archivo):
    limite = LIMITE_IMAGEN_MB * 1024 * 1024
    if archivo.size > limite:
        raise ValidationError(f"La imagen no puede superar los {LIMITE_IMAGEN_MB} MB.")


def validar_tamano_pdf(archivo):
    limite = LIMITE_PDF_MB * 1024 * 1024
    if archivo.size > limite:
        raise ValidationError(f"El archivo no puede superar los {LIMITE_PDF_MB} MB.")
