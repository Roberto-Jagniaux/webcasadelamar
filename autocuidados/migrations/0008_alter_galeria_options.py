# Generated by Django 4.1 on 2024-09-04 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autocuidados', '0007_alter_galeria_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='galeria',
            options={'verbose_name': 'imagen', 'verbose_name_plural': 'imagenes'},
        ),
    ]
