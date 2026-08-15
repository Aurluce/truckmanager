from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[('measurements','0001_initial')]
    operations=[migrations.AddField(model_name='fuelmeasurement',name='fuel_consumed_liters',field=models.FloatField(default=0))]
