# Generated by Django 2.0.1 on 2018-02-20 20:08

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataProviderProcessor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('sequence', 'sequence'), ('grid', 'grid')], max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='NamedStorm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('geo', django.contrib.gis.db.models.fields.GeometryField(geography=True, srid=4326)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='NamedStormCoveredData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
                ('geo', django.contrib.gis.db.models.fields.GeometryField(geography=True, srid=4326)),
                ('named_storm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='named_storms.NamedStorm')),
            ],
        ),
        migrations.CreateModel(
            name='NamedStormCoveredDataProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('url', models.CharField(max_length=500)),
                ('active', models.BooleanField()),
                ('covered_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='named_storms.NamedStormCoveredData')),
                ('processor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='named_storms.DataProviderProcessor')),
            ],
        ),
    ]