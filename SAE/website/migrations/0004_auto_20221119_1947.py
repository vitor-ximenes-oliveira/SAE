# Generated by Django 3.2.13 on 2022-11-19 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_remove_formulario_fkturmas'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostasformulario',
            name='ano_letivo',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='respostasformulario',
            name='classe',
            field=models.CharField(default='', max_length=30),
        ),
    ]
