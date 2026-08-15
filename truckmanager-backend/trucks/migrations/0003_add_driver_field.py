from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trucks', '0002_device_and_thresholds'),
    ]

    operations = [
        migrations.AddField(
            model_name='truck',
            name='driver',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='driven_trucks',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Conducteur'
            ),
        ),
    ]
