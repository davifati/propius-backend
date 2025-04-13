import json
import os
from django.core.management.base import BaseCommand
from django.core.management.color import Style


class Command(BaseCommand):
    help = """
    Creates separate JSON files for each model block in the fixture data.
    
    This command:
    1. Reads the fixture file
    2. Groups the data by model
    3. Creates a JSON file named after each model containing its data
    
    Example:
    python manage.py make_fixture --fixture mysql_fixture.json
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture", required=True, help="Path to the fixture file to read"
        )

    def handle(self, *args, **options):
        fixture_path = options["fixture"]

        # Check if fixture exists
        if not os.path.exists(fixture_path):
            self.stdout.write(
                self.style.ERROR(f"Fixture file not found: {fixture_path}")
            )
            return

        # Load fixture data
        self.stdout.write(f"Reading fixture from {fixture_path}...")
        with open(fixture_path, "r") as f:
            fixture_data = json.load(f)

        # Group data by model
        model_data = {}
        for item in fixture_data:
            model_name = item["model"]
            if model_name not in model_data:
                model_data[model_name] = []
            model_data[model_name].append(item)

        # Create output directory if it doesn't exist
        output_dir = "fixtures"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create JSON file for each model block
        for model_name, items in model_data.items():
            if items:
                output_path = os.path.join(output_dir, f"{model_name}.json")
                with open(output_path, "w") as f:
                    json.dump(items, f, indent=2)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {model_name}.json with {len(items)} items"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Model {model_name} has no items")
                )

        self.stdout.write("\n" + self.style.SUCCESS("Done!"))
