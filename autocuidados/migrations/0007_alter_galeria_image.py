# Generated by Django 4.1 on 2024-09-03 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autocuidados', '0006_galeria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galeria',
            name='image',
            field=models.ImageField(upload_to='autocuidados'),
        ),
    ]
