from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Crea categorías (Duradry, Xerac, Drysol) y productos iniciales.'

    def handle(self, *args, **options):
        categories_data = [
            {'name': 'Duradry', 'slug': 'duradry', 'description': 'Productos Duradry para sudoración.'},
            {'name': 'Xerac', 'slug': 'xerac', 'description': 'Productos Xerac AC.'},
            {'name': 'Drysol', 'slug': 'drysol', 'description': 'Productos Drysol.'},
        ]
        for data in categories_data:
            cat, created = Category.objects.get_or_create(slug=data['slug'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoría creada: {cat.name}'))

        products_data = [
            {'name': 'Duradry Barra AM', 'slug': 'barra-am', 'category_slug': 'duradry', 'price': 21.99, 'old_price': 35.99, 'sku': 'DUR-BARRA-AM', 'description': 'Desodorante antitranspirante de fuerza clínica. Fórmula limpia con ingredientes naturales.', 'is_featured': True},
            {'name': 'Xerac AC Antitranspirante 35ML', 'slug': 'xerac-ac', 'category_slug': 'xerac', 'price': 24.99, 'old_price': None, 'sku': 'XER-AC-35', 'description': 'Antitranspirante clínico Xerac AC en presentación 35 ml.', 'is_featured': True},
            {'name': 'Drysol', 'slug': 'drysol', 'category_slug': 'drysol', 'price': 18.99, 'old_price': 22.99, 'sku': 'DRY-001', 'description': 'Solución para hiperhidrosis. Eficacia comprobada.', 'is_best_seller': True},
            {'name': 'Duradry Wash', 'slug': 'wash', 'category_slug': 'duradry', 'price': 19.99, 'old_price': None, 'sku': 'DUR-WASH', 'description': 'Gel de baño Duradry para cuidado corporal.', 'is_featured': False},
            {'name': 'Desodorante Corporal Duradry', 'slug': 'desodorante-corporal', 'category_slug': 'duradry', 'price': 22.99, 'old_price': None, 'sku': 'DUR-CORP', 'description': 'Desodorante corporal de amplio espectro.', 'is_featured': False},
        ]
        for data in products_data:
            category_slug = data.pop('category_slug')
            cat = Category.objects.get(slug=category_slug)
            slug = data.pop('slug')
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    **data,
                    'category': cat,
                    'stock': 100,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Producto creado: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Seed completado.'))
