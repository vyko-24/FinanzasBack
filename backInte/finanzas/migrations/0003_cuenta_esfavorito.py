# Generated by Django 5.1.5 on 2025-03-30 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finanzas', '0002_gasto_cuenta'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuenta',
            name='esFavorito',
            field=models.BooleanField(default=False),
        ),
    ]
