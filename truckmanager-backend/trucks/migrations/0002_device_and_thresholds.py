from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[('trucks','0001_initial')]
    operations=[
        migrations.AddField(model_name='truck',name='esp32_device_id',field=models.CharField(max_length=80,blank=True,null=True,unique=True)),
        migrations.AddField(model_name='truck',name='esp32_mac_address',field=models.CharField(max_length=32,blank=True,null=True)),
        migrations.AddField(model_name='truck',name='firmware_version',field=models.CharField(max_length=40,blank=True,default='')),
        migrations.AddField(model_name='truck',name='api_key',field=models.CharField(max_length=128,blank=True,null=True,unique=True)),
        migrations.AddField(model_name='truck',name='low_fuel_threshold_percent',field=models.FloatField(default=15)),
        migrations.AddField(model_name='truck',name='speed_limit_kmh',field=models.FloatField(default=90)),
    ]
