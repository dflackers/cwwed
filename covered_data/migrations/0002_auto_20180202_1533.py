# Generated by Django 2.0.1 on 2018-02-02 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covered_data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='covereddata',
            name='name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='covereddataprovider',
            name='output',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='namedstorm',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]