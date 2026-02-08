# Generated for order extended fields and OrderMessage

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='document',
            field=models.CharField(blank=True, max_length=50, verbose_name='Cédula/RIF/Pasaporte'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('delivery_caracas', 'Delivery Caracas'),
                    ('delivery_national', 'Envío nacional'),
                    ('office_pickup', 'Retiro en oficina'),
                ],
                default='delivery_caracas',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_agency',
            field=models.CharField(
                blank=True,
                choices=[
                    ('mrw', 'MRW'),
                    ('domesa', 'DOMESA'),
                    ('zoom', 'ZOOM'),
                    ('tealca', 'TEALCA'),
                    ('dhl', 'DHL'),
                    ('', 'N/A'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='office_pickup',
            field=models.BooleanField(default=False, verbose_name='Retiro en oficina'),
        ),
        migrations.AddField(
            model_name='order',
            name='central_address',
            field=models.TextField(blank=True, verbose_name='Dirección corta y céntrica'),
        ),
        migrations.CreateModel(
            name='OrderMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_from_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='orders.order')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
