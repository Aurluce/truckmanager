from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('trucks', '0003_add_driver_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='truck',
            name='fuel_tolerance_threshold_l',
            field=models.FloatField(default=2.0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='truck',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="Prix d'achat"),
        ),
        migrations.AddField(
            model_name='truck',
            name='tco_months',
            field=models.IntegerField(default=12, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Durée TCO (mois)'),
        ),
    ]
