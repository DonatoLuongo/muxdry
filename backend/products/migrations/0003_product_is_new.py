# Generated manually for add_is_new

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_image_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Etiqueta Nuevo'),
        ),
    ]
