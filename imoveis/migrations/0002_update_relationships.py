from django.db import migrations, models
import django.db.models.deletion


def link_condominios_to_administradoras(apps, schema_editor):
    """
    Link existing condominios to administradoras based on administradoracondominio_id
    """
    Condominio = apps.get_model("imoveis", "Condominio")
    Administradora = apps.get_model("imoveis", "Administradora")

    for condominio in Condominio.objects.all():
        if condominio.administradoracondominio_id:
            try:
                administradora = Administradora.objects.get(
                    id=condominio.administradoracondominio_id
                )
                condominio.administradora = administradora
                condominio.save()
            except Administradora.DoesNotExist:
                # If administradora doesn't exist, create a default one
                default_admin = Administradora.objects.create(
                    nome=f"Administradora {condominio.administradoracondominio_id}",
                    email="",
                    telefone="",
                )
                condominio.administradora = default_admin
                condominio.save()


def link_unidades_to_condominios(apps, schema_editor):
    """
    Link existing unidades to condominios based on administracaocondominio_id
    """
    Unidade = apps.get_model("imoveis", "Unidade")
    Condominio = apps.get_model("imoveis", "Condominio")

    for unidade in Unidade.objects.all():
        # Fix empty unidade field
        print(">>>>", unidade.unidade)
        print(">>>>", type(unidade.unidade))

        try:
            unidade.unidade = int(unidade.unidade)
        except ValueError:
            unidade.unidade = None
            unidade.save()

        # ValueError: invalid literal for int() with base 10: ''
        if unidade.unidade == "":
            unidade.unidade = None
            unidade.save()

        if unidade.unidade is None:
            unidade.unidade = 0
            unidade.save()

        if unidade.unidade is not None:
            unidade.unidade = int(unidade.unidade)
            unidade.save()

        if unidade.administracaocondominio_id:
            try:
                condominio = Condominio.objects.get(
                    id=unidade.administracaocondominio_id
                )
                unidade.condominio = condominio
                unidade.save()
            except Condominio.DoesNotExist:
                # If condominio doesn't exist, create a default one
                try:
                    # Try to get an existing administradora
                    administradora = apps.get_model(
                        "imoveis", "Administradora"
                    ).objects.first()
                    if not administradora:
                        # Create a default administradora if none exists
                        administradora = apps.get_model(
                            "imoveis", "Administradora"
                        ).objects.create(
                            nome="Administradora Padrão", email="", telefone=""
                        )

                    default_cond = Condominio.objects.create(
                        nome=f"Condomínio {unidade.administracaocondominio_id}",
                        endereco="",
                        cep="",
                        administradora=administradora,
                    )
                    unidade.condominio = default_cond
                    unidade.save()
                except Exception as e:
                    # If anything goes wrong, just skip this record
                    print(f"Error processing unidade {unidade.id}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ("imoveis", "0001_initial"),
    ]

    operations = [
        # First, make the ID fields nullable to allow for a smooth transition
        migrations.AlterField(
            model_name="condominio",
            name="administradoracondominio_id",
            field=models.IntegerField(
                blank=True,
                help_text="ID da administradora a qual o condomínio faz parte",
                null=True,
                verbose_name="ID da administradora",
            ),
        ),
        migrations.AlterField(
            model_name="unidade",
            name="administracaocondominio_id",
            field=models.IntegerField(
                blank=True,
                help_text="ID do condomínio a qual a Unidade faz parte",
                null=True,
                verbose_name="ID do condomínio",
            ),
        ),
        # Make unidade field nullable
        migrations.AlterField(
            model_name="unidade",
            name="unidade",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Número da Unidade",
            ),
        ),
        # Update pasta field to be a CharField with proper attributes
        migrations.AlterField(
            model_name="unidade",
            name="pasta",
            field=models.CharField(
                max_length=20,
                blank=True,
                null=True,
                unique=True,
                verbose_name="Número da Pasta",
            ),
        ),
        # Add the new ForeignKey fields
        migrations.AddField(
            model_name="condominio",
            name="administradora",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="condominios",
                to="imoveis.administradora",
                verbose_name="Administradora da qual o condomínio faz parte",
                help_text="Refere-se à administradora responsável por esse condomínio.",
            ),
        ),
        migrations.AddField(
            model_name="unidade",
            name="condominio",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="unidades",
                to="imoveis.condominio",
                verbose_name="Condomínio da qual a unidade faz parte",
                help_text="Refere-se ao condomínio ao qual esta unidade pertence.",
            ),
        ),
        # Run the data migration to link existing records
        migrations.RunPython(link_condominios_to_administradoras),
        migrations.RunPython(link_unidades_to_condominios),
        # Make the ForeignKey fields required
        migrations.AlterField(
            model_name="condominio",
            name="administradora",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="condominios",
                to="imoveis.administradora",
                verbose_name="Administradora da qual o condomínio faz parte",
                help_text="Refere-se à administradora responsável por esse condomínio.",
            ),
        ),
        migrations.AlterField(
            model_name="unidade",
            name="condominio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="unidades",
                to="imoveis.condominio",
                verbose_name="Condomínio da qual a unidade faz parte",
                help_text="Refere-se ao condomínio ao qual esta unidade pertence.",
            ),
        ),
    ]
