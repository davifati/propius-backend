# Generated by Django 5.2 on 2025-04-10 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0015_alter_unidade_unidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidade',
            name='unidade',
            field=models.IntegerField(blank=True, null=True, verbose_name='Número da Unidade'),
        ),
    ]
