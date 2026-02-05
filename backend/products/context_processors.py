# products/context_processors.py
"""Context processors para templates - hace que 'categories' esté disponible en todas las páginas."""

from .models import Category


def categories(request):
    """Añade las categorías al contexto de todos los templates."""
    return {
        'categories': Category.objects.all(),
    }
