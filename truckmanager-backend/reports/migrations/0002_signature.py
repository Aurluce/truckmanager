from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[('reports','0001_initial')]
    operations=[migrations.AddField(model_name='report',name='signature_hash',field=models.CharField(max_length=64,blank=True,default=''))]
