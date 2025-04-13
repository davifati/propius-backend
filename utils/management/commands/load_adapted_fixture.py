import json
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction, connection
from django.apps import apps
from pathlib import Path
from django.core.serializers.json import Deserializer


class Command(BaseCommand):
    help = """
    Load and adapt fixture data from MySQL to your Django models.
    
    This command:
    1. Loads the fixture data
    2. Transforms it according to your mapping rules
    3. Saves it to your Django models
    
    Example:
    python manage.py load_adapted_fixture --fixture mysql_fixture.json --mapping mapping.json --order "administradoracondominios,administracaocondominios"
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture", required=True, help="Path to the fixture file to load"
        )
        parser.add_argument(
            "--mapping", help="Path to a JSON file with field mappings (optional)"
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before loading"
        )
        parser.add_argument(
            "--order",
            help='Comma-separated list of models to load in order (e.g., "model1,model2,model3")',
        )
        parser.add_argument(
            "--disable-constraints",
            action="store_true",
            help="Temporarily disable foreign key constraints during loading",
        )

    def handle(self, *args, **options):
        fixture_path = options["fixture"]
        mapping_path = options.get("mapping")
        clear_existing = options.get("clear", False)
        model_order = (
            options.get("order", "").split(",") if options.get("order") else None
        )
        disable_constraints = options.get("disable_constraints", False)

        # Check if fixture exists
        if not os.path.exists(fixture_path):
            self.stdout.write(
                self.style.ERROR(f"Fixture file not found: {fixture_path}")
            )
            return

        # Load mapping if provided
        field_mapping = {}
        if mapping_path and os.path.exists(mapping_path):
            with open(mapping_path, "r") as f:
                field_mapping = json.load(f)

        # Load fixture data
        self.stdout.write(f"Loading fixture from {fixture_path}...")
        with open(fixture_path, "r") as f:
            fixture_data = json.load(f)

        # Group data by model
        model_data = {}
        for item in fixture_data:
            model_name = item["model"]
            if model_name not in model_data:
                model_data[model_name] = []
            model_data[model_name].append(item)

        # Disable foreign key constraints if requested
        if disable_constraints:
            self.stdout.write("Disabling foreign key constraints...")
            self._disable_foreign_key_constraints()

        try:
            # Clear existing data if requested
            if clear_existing:
                self.stdout.write("Clearing existing data...")
                self._clear_existing_data(fixture_data, mapping_path, field_mapping)

            # Process and load data in specified order
            if model_order:
                self.stdout.write(f"Loading models in order: {', '.join(model_order)}")
                for model_name in model_order:
                    if model_name in model_data:
                        # Use a separate transaction for each model to avoid conflicts
                        with transaction.atomic():
                            self._load_model_data(
                                model_name, model_data[model_name], field_mapping
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Model {model_name} not found in fixture data"
                            )
                        )
            else:
                # Load all models
                for model_name, items in model_data.items():
                    # Use a separate transaction for each model to avoid conflicts
                    with transaction.atomic():
                        self._load_model_data(model_name, items, field_mapping)

            self.stdout.write(
                self.style.SUCCESS("Successfully loaded and adapted fixture data")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading fixture data: {str(e)}"))
            # Re-raise the exception to ensure proper error handling
            raise
        finally:
            # Re-enable foreign key constraints if they were disabled
            if disable_constraints:
                self.stdout.write("Re-enabling foreign key constraints...")
                self._enable_foreign_key_constraints()

    def _load_model_data(self, model_name, items, field_mapping):
        """
        Load data for a specific model.
        """
        from django.apps import apps
        from django.core.serializers.json import Deserializer
        from django.db import transaction

        self.stdout.write(f"Loading data for {model_name}...")

        # Get mapping info for this model
        model_mapping = field_mapping.get(model_name, {})
        app_name = model_mapping.get("app")
        django_model_name = model_mapping.get("model")
        field_mappings = model_mapping.get("fields", {})

        if not app_name or not django_model_name:
            self.stdout.write(
                self.style.WARNING(
                    f"No mapping found for model {model_name}, using default..."
                )
            )
            django_model_name = model_name

        # Get the Django model to check field existence
        try:
            full_model_name = f"{app_name}.{django_model_name}"
            model = apps.get_model(full_model_name)
            model_fields = [f.name for f in model._meta.fields]
        except LookupError:
            self.stdout.write(
                self.style.WARNING(f"Model not found: {full_model_name}, skipping...")
            )
            return

        # Adapt the data
        adapted_data = []
        for item in items:
            fields = item["fields"]
            adapted_fields = {}

            # Apply field mappings if available
            for old_field, new_field in field_mappings.items():
                if old_field in fields:
                    # Special handling for foreign key to Administradora
                    if (
                        old_field == "administradoracondominio_id"
                        and new_field == "administradora"
                    ):
                        # Try to find the corresponding Administradora
                        try:
                            Administradora = apps.get_model(app_name, "Administradora")

                            # Try to find by email or name if available
                            admin_email = fields.get("email", "")
                            admin_name = fields.get("nome", "")

                            if admin_email:
                                admin = Administradora.objects.filter(
                                    email=admin_email
                                ).first()
                            elif admin_name:
                                admin = Administradora.objects.filter(
                                    nome=admin_name
                                ).first()
                            else:
                                admin = None

                            if admin:
                                adapted_fields[new_field] = admin.id
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Could not find Administradora for {model_name} with ID {fields.get(old_field)}"
                                    )
                                )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error finding Administradora: {str(e)}"
                                )
                            )
                    else:
                        # Check if the field exists in the model
                        if new_field in model_fields:
                            # Handle empty values for integer fields
                            if new_field == "id" and fields[old_field] == "":
                                # Skip empty ID fields - Django will generate a new ID
                                continue
                            adapted_fields[new_field] = fields[old_field]
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Field {new_field} does not exist in model {full_model_name}, skipping..."
                                )
                            )

            # Use the correct model name format for Django
            full_model_name = (
                f"{app_name}.{django_model_name}" if app_name else django_model_name
            )

            adapted_data.append({"model": full_model_name, "fields": adapted_fields})

        # Save to temporary fixture
        temp_fixture = f"temp_{model_name}.json"
        try:
            with open(temp_fixture, "w") as f:
                json.dump(adapted_data, f, indent=2)

            # Load the data directly using Django's ORM
            with open(temp_fixture, "r") as f:
                for obj in Deserializer(f):
                    try:
                        obj.save()
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error saving object {obj.object}: {str(e)}"
                            )
                        )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error loading data for {model_name}: {str(e)}")
            )
            # Re-raise the exception to ensure proper error handling
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_fixture):
                try:
                    os.remove(temp_fixture)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Error removing temporary file {temp_fixture}: {str(e)}"
                        )
                    )

    def _adapt_data(self, fixture_data, field_mapping):
        """
        Adapt the fixture data according to the mapping rules.
        """
        adapted_data = []

        for item in fixture_data:
            model_name = item["model"]
            fields = item["fields"]

            # Get mapping info for this model
            model_mapping = field_mapping.get(model_name, {})
            app_name = model_mapping.get("app")
            django_model_name = model_mapping.get("model")

            if not app_name or not django_model_name:
                self.stdout.write(
                    self.style.WARNING(
                        f"No mapping found for model {model_name}, skipping..."
                    )
                )
                continue

            # Use the correct model name format for Django
            full_model_name = f"{app_name}.{django_model_name}"

            # Get the Django model
            try:
                model = apps.get_model(full_model_name)
            except LookupError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Model not found: {full_model_name}, skipping..."
                    )
                )
                continue

            # Apply field mappings if available
            if model_name in field_mapping:
                for old_field, new_field in field_mapping[model_name].items():
                    if old_field in fields:
                        # Handle empty values for integer fields
                        if new_field == "id" and fields[old_field] == "":
                            # Skip empty ID fields - Django will generate a new ID
                            continue
                        fields[new_field] = fields.pop(old_field)

            # Add the adapted item
            adapted_data.append({"model": full_model_name, "fields": fields})

        return adapted_data

    def _clear_existing_data(self, fixture_data, mapping_path, field_mapping):
        """
        Clear existing data for the models in the fixture.
        """
        # Group data by model to avoid clearing the same model multiple times
        models_to_clear = set()
        for item in fixture_data:
            model_name = item["model"]
            models_to_clear.add(model_name)

        try:
            with transaction.atomic():
                for model_name in models_to_clear:
                    try:
                        # Get mapping info for this model
                        model_mapping = field_mapping.get(model_name, {})
                        app_name = model_mapping.get("app")
                        django_model_name = model_mapping.get("model")

                        if not app_name or not django_model_name:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"No mapping found for model {model_name}, skipping..."
                                )
                            )
                            continue

                        # Use the correct model name format for Django
                        full_model_name = f"{app_name}.{django_model_name}"
                        model = apps.get_model(full_model_name)
                        model.objects.all().delete()
                        self.stdout.write(f"Cleared data for {full_model_name}")
                    except LookupError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Model not found: {model_name}, skipping..."
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error clearing data for {model_name}: {str(e)}"
                            )
                        )
                        # Don't re-raise the exception, just log it and continue
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in transaction: {str(e)}"))
            # Re-raise the exception to ensure the transaction is rolled back
            raise

    def _disable_foreign_key_constraints(self):
        """
        Temporarily disable foreign key constraints.
        """
        with connection.cursor() as cursor:
            if connection.vendor == "sqlite":
                cursor.execute("PRAGMA foreign_keys=OFF;")
            elif connection.vendor == "mysql":
                cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            elif connection.vendor == "postgresql":
                cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Foreign key constraint disabling not supported for {connection.vendor}"
                    )
                )

    def _enable_foreign_key_constraints(self):
        """
        Re-enable foreign key constraints.
        """
        with connection.cursor() as cursor:
            if connection.vendor == "sqlite":
                cursor.execute("PRAGMA foreign_keys=ON;")
            elif connection.vendor == "mysql":
                cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            elif connection.vendor == "postgresql":
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Foreign key constraint enabling not supported for {connection.vendor}"
                    )
                )
