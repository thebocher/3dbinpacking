# Generated by Django 4.2.4 on 2023-08-07 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='x',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='y',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='z',
            field=models.FloatField(),
        ),
    ]
