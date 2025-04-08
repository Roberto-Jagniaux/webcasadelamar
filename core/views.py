from django.shortcuts import render

# Create your views here.

def psicoterapia(request):
    return render(request,"core/psicoterapia.html")

def inicio(request):
    return render(request,"core/inicio.html")

def escuelaparaelbuentrato(request):
    return render(request,"core/escuelaparaelbuentrato.html")



def contact(request):
    return render(request,"core/contact.html")

def recursosgratuitos(request):
    return render(request,"core/recursosgratuitos.html")