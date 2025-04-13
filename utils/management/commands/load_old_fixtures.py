import json
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps


class Command(BaseCommand):
    help = """
    Loads fixtures from a JSON file into the current database.
    
    Example:
    python manage.py load_old_fixtures --input fixtures.json
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Path to the JSON fixtures file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before loading fixtures",
        )

    def handle(self, *args, **options):
        input_file = options["input"]
        clear_existing = options["clear"]

        if not os.path.exists(input_file):
            self.stderr.write(
                self.style.ERROR(f"Fixtures file not found: {input_file}")
            )
            return

        self.stdout.write(f"Loading fixtures from: {input_file}")

        with open(input_file, "r") as f:
            fixtures = json.load(f)

        # Get all tables from the current database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%'"
            )
            current_tables = [row[0] for row in cursor.fetchall()]

        # Clear existing data if requested
        if clear_existing:
            self.stdout.write("Clearing existing data...")
            with transaction.atomic():
                for table in current_tables:
                    if table in fixtures:
                        self.stdout.write(f"  Clearing table: {table}")
                        cursor.execute(f"DELETE FROM {table}")

        # Load fixtures into the current database
        self.stdout.write("Loading fixtures into the current database...")
        with transaction.atomic():
            for table, data in fixtures.items():
                if not data:
                    self.stdout.write(f"  No data to load for table: {table}")
                    continue

                # Check if table exists in the current database
                if table not in current_tables:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Table not found in current database: {table}"
                        )
                    )
                    continue

                # Get column names from the first row
                if not data:
                    continue

                columns = list(data[0].keys())
                placeholders = ", ".join(["?" for _ in columns])
                column_names = ", ".join(columns)

                # Insert data into the table
                self.stdout.write(f"  Loading {len(data)} rows into table: {table}")
                with connection.cursor() as cursor:
                    for row in data:
                        values = [row.get(col) for col in columns]
                        cursor.execute(
                            f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})",
                            values,
                        )

        self.stdout.write(
            self.style.SUCCESS("Successfully loaded fixtures into the current database")
        )
