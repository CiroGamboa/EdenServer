# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-03 21:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genEden', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maceta',
            name='tipoPlanta',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='macetas_planta', to='genEden.Planta'),
        ),
    ]
