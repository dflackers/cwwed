# Generated by Django 2.0.1 on 2018-02-12 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('covered_data', '0020_dataproviderprocessor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataproviderprocessor',
            old_name='processor_class',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='namedstormcovereddataprovider',
            name='provider_class',
        ),
        migrations.AddField(
            model_name='namedstormcovereddataprovider',
            name='processor_class',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='covered_data.DataProviderProcessor'),
            preserve_default=False,
        ),
    ]