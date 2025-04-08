# Generated by Django 4.1 on 2024-07-17 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cursos',
            fields=[
                ('idC', models.AutoField(primary_key=True, serialize=False, verbose_name='ID curso')),
                ('nomC', models.CharField(max_length=80, verbose_name='Nombre de curso')),
                ('image', models.ImageField(upload_to='projects')),
                ('desC', models.TextField(verbose_name='Descripcion')),
                ('durC', models.CharField(max_length=80, verbose_name='Duración de curso')),
                ('modC', models.CharField(choices=[('presencial', 'Presencial'), ('online', 'Online'), ('Semipresencial', 'Semipresencial')], max_length=15, verbose_name='Modalidad de curso')),
                ('valorC', models.CharField(max_length=80, verbose_name='Valor de curso')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
            },
        ),
    ]
