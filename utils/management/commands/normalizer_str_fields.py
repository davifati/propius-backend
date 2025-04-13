import re
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import models


class Command(BaseCommand):
    help = "Cleans string fields in a model by removing special characters and converting to lowercase"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label", type=str, help="App label containing the model"
        )
        parser.add_argument("model_name", type=str, help="Name of the model to clean")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def clean_string(self, value):
        """Remove special characters and convert to lowercase."""
        if not isinstance(value, str):
            return value

        # Remove accents
        import unicodedata

        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

        # Remove special characters, keep only alphanumeric and spaces
        value = re.sub(r"[^a-zA-Z0-9\s]", "", value)

        # Convert to lowercase
        return value.lower()

    def handle(self, *args, **options):
        app_label = options["app_label"]
        model_name = options["model_name"]
        dry_run = options["dry_run"]

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise CommandError(f"Model '{model_name}' in app '{app_label}' not found.")

        # Get all string fields from the model
        string_fields = []
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                string_fields.append(field.name)

        if not string_fields:
            self.stdout.write(
                self.style.WARNING(f"No string fields found in model '{model_name}'")
            )
            return

        self.stdout.write(
            f"Found {len(string_fields)} string fields in model '{model_name}': {', '.join(string_fields)}"
        )

        # Get all objects from the model
        objects = model.objects.all()
        count = objects.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING(f"No objects found in model '{model_name}'")
            )
            return

        self.stdout.write(f"Processing {count} objects...")

        updated_count = 0
        for obj in objects:
            updated = False
            updates = {}

            for field_name in string_fields:
                current_value = getattr(obj, field_name)
                if current_value is None:
                    continue

                cleaned_value = self.clean_string(current_value)

                if cleaned_value != current_value:
                    updates[field_name] = cleaned_value
                    updated = True

            if updated:
                if dry_run:
                    self.stdout.write(f"Would update {model_name} (id={obj.id}):")
                    for field, new_value in updates.items():
                        old_value = getattr(obj, field)
                        self.stdout.write(f"  {field}: '{old_value}' -> '{new_value}'")
                else:
                    for field, value in updates.items():
                        setattr(obj, field, value)
                    obj.save(update_fields=list(updates.keys()))
                    updated_count += 1

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete. Would update {updated_count} objects."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {updated_count} objects.")
            )
