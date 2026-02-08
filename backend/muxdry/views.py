from django.http import HttpResponse
from django.shortcuts import render


def health_check_view(request):
    """Ruta para el health check de Render (monitoreo del servicio)."""
    return HttpResponse("ok", content_type="text/plain")


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def preview_404_view(request):
    """Vista para previsualizar la página 404 durante desarrollo (DEBUG=True)."""
    return render(request, '404.html', status=404)
