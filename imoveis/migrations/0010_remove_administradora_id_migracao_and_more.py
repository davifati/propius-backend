# Generated by Django 5.2 on 2025-04-10 22:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0009_alter_unidade_options_remove_unidade_condominio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='administradora',
            name='id_migracao',
        ),
        migrations.RemoveField(
            model_name='condominio',
            name='id_migracao',
        ),
        migrations.RemoveField(
            model_name='unidade',
            name='id_migracao',
        ),
    ]
