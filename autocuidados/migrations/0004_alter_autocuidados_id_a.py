# Generated by Django 4.1 on 2024-09-03 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autocuidados', '0003_alter_autocuidados_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autocuidados',
            name='id_a',
            field=models.CharField(default='0', max_length=10, primary_key=True, serialize=False, verbose_name='ID autocuidado'),
        ),
    ]
