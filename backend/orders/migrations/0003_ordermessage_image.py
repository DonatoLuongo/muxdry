# Generated manually - OrderMessage.image for payment proof

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_extended_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermessage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='order_messages/%Y/%m/', verbose_name='Comprobante de pago'),
        ),
    ]
