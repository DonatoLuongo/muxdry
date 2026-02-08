# Generated manually - OrderMessage.read_by_admin_at for admin unread notification

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_ordermessage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermessage',
            name='read_by_admin_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
