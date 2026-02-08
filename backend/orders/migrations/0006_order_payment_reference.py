# Generated manually for invoice reference number

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_encrypt_ordermessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_reference',
            field=models.CharField(blank=True, max_length=120, verbose_name='Nº de referencia del comprobante'),
        ),
    ]
