# Generated by Django 2.0.1 on 2018-02-02 18:22

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('covered_data', '0005_namedstorm_poly'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='namedstorm',
            name='poly',
        ),
        migrations.AddField(
            model_name='namedstorm',
            name='geo',
            field=django.contrib.gis.db.models.fields.GeometryField(geography=True, null=True, srid=4326),
        ),
    ]
