from django import template
from django.templatetags.static import static

register = template.Library()

# Fallback: slug -> ruta en assets/products/
SLUG_IMAGE_PATHS = {
    'barra-am': 'assets/products/Barra-Antitranspirante/Barra-Duradry.png',
    'duradry-barra': 'assets/products/Barra-Antitranspirante/Barra-Duradry.png',
    'xerac-ac': 'assets/products/Xerac_AC/Xerac-Antitranspirante.png',
    'xerac': 'assets/products/Xerac_AC/Xerac.png',
    'drysol': 'assets/products/Drysol/Drysol.png',
    'wash': 'assets/products/Duradry-WASH/Duradry-Gel.png',
    'duradry-wash': 'assets/products/Duradry-WASH/Duradry-Gel.png',
    'desodorante-corporal': 'assets/products/Desodorant-Corporal/Duradry-Corporal.png',
}

# Imagen alternativa para hover (cuando no hay image_hover en el modelo)
SLUG_HOVER_IMAGE_PATHS = {
    'barra-am': 'assets/products/Barra-Antitranspirante/Barra-Clinica.jpg',
    'duradry-barra': 'assets/products/Barra-Antitranspirante/Barra.jpg',
    'xerac-ac': 'assets/products/Xerac_AC/Xerac-2.png',
    'xerac': 'assets/products/Xerac_AC/Xerac-Antitranspirante.png',
    'drysol': 'assets/products/Drysol/Drysol-2.png',
    'wash': 'assets/products/Duradry-WASH/Duradry-2.jpg',
    'duradry-wash': 'assets/products/Duradry-WASH/Gel-Baño.png',
    'desodorante-corporal': 'assets/products/Desodorant-Corporal/Duradry-Corporal2.png',
}

# Galería: hasta 3 imágenes por producto (slug -> [img1, img2, img3])
SLUG_GALLERY_IMAGES = {
    'barra-am': ['assets/products/Barra-Antitranspirante/Barra-Duradry.png', 'assets/products/Barra-Antitranspirante/Barra-Clinica.jpg', 'assets/products/Barra-Antitranspirante/Barra.jpg'],
    'duradry-barra': ['assets/products/Barra-Antitranspirante/Barra-Duradry.png', 'assets/products/Barra-Antitranspirante/Barra-Clinica.jpg', 'assets/products/Barra-Antitranspirante/Barra.jpg'],
    'xerac-ac': ['assets/products/Xerac_AC/Xerac-Antitranspirante.png', 'assets/products/Xerac_AC/Xerac-2.png', 'assets/products/Xerac_AC/Xerac.png'],
    'xerac': ['assets/products/Xerac_AC/Xerac.png', 'assets/products/Xerac_AC/Xerac-Antitranspirante.png', 'assets/products/Xerac_AC/Xerac-2.png'],
    'drysol': ['assets/products/Drysol/Drysol.png', 'assets/products/Drysol/Drysol-2.png', 'assets/products/Drysol/Drysol-3.png'],
    'wash': ['assets/products/Duradry-WASH/Duradry-Gel.png', 'assets/products/Duradry-WASH/Duradry-2.jpg', 'assets/products/Duradry-WASH/Gel-Baño.png'],
    'duradry-wash': ['assets/products/Duradry-WASH/Duradry-Gel.png', 'assets/products/Duradry-WASH/Duradry-2.jpg', 'assets/products/Duradry-WASH/Gel-Baño.png'],
    'desodorante-corporal': ['assets/products/Desodorant-Corporal/Duradry-Corporal.png', 'assets/products/Desodorant-Corporal/Duradry-Corporal2.png', 'assets/products/Desodorant-Corporal/Desodorante-Duradry-Corporal.png'],
}

DEFAULT_PRODUCT_IMAGE = 'assets/products/PROXI.png'


@register.simple_tag
def product_image_url(product):
    """Devuelve la URL de la imagen del producto (subida o fallback por slug)."""
    if product and product.image:
        return product.image.url
    if product and getattr(product, 'slug', None):
        path = SLUG_IMAGE_PATHS.get(product.slug, DEFAULT_PRODUCT_IMAGE)
        return static(path)
    return static(DEFAULT_PRODUCT_IMAGE)


@register.simple_tag
def product_hover_image_url(product):
    """Devuelve la URL de la imagen hover (subida, alternativa por slug, o misma que principal)."""
    if product and getattr(product, 'image_hover', None) and product.image_hover:
        return product.image_hover.url
    # Si hay slug y tenemos imagen hover alternativa por slug, usarla para que el hover se note
    if product and getattr(product, 'slug', None):
        hover_path = SLUG_HOVER_IMAGE_PATHS.get(product.slug)
        if hover_path:
            return static(hover_path)
        path = SLUG_IMAGE_PATHS.get(product.slug, DEFAULT_PRODUCT_IMAGE)
        return static(path)
    if product and product.image:
        return product.image.url
    return static(DEFAULT_PRODUCT_IMAGE)


@register.simple_tag
def product_gallery_urls(product):
    """
    Devuelve lista de hasta 3 URLs de imágenes para la galería del detalle.
    Usa SLUG_GALLERY_IMAGES o fallback a imagen principal/hover.
    """
    urls = []
    slug = getattr(product, 'slug', None) if product else None
    if slug and slug in SLUG_GALLERY_IMAGES:
        for path in SLUG_GALLERY_IMAGES[slug][:3]:
            urls.append(static(path))
    else:
        main = product_image_url(product)
        hover = product_hover_image_url(product)
        urls = [main]
        if hover != main:
            urls.append(hover)
        while len(urls) < 3:
            urls.append(main)
    return urls[:3]
