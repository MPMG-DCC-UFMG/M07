# Generated by Django 3.0.5 on 2020-10-18 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_searchableindicesconfigs_index_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='compare',
            field=models.CharField(choices=[('regular', 'Regular'), ('replica', 'Replicas')], default='', max_length=10),
        ),
        migrations.AddField(
            model_name='searchableindicesconfigs',
            name='group',
            field=models.CharField(choices=[('regular', 'Regular'), ('replica', 'Replicas')], default='regular', max_length=10),
            preserve_default=False,
        ),
    ]