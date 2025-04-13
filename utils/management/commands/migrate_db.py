import os
import json
import sqlite3
import pymysql
import psycopg2
import datetime
import decimal
import psycopg2.extras
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection, transaction
from django.apps import apps
from pathlib import Path


class Command(BaseCommand):
    help = """
    Extract data from database into Django fixtures.
    
    Examples:
    1. Extract all tables:
        python manage.py migrate_db --source-type mysql --host localhost --database your_db --user your_user --password your_password --output-file data.json
        python manage.py migrate_db --source-type sqlite --source-file /path/to/your/database.sqlite3 --output-file data.json
    
    2. Extract specific tables:
        python manage.py migrate_db --source-type mysql --host localhost --database your_db --user your_user --password your_password --tables monitoramento_imovel,imoveis_contrato --output-file data.json
        python manage.py migrate_db --source-type sqlite --source-file /path/to/your/database.sqlite3 --tables monitoramento_imovel,imoveis_contrato --output-file data.json
        
    3. Extract tables from specific apps:
        python manage.py migrate_db --source-type mysql --host localhost --database your_db --user your_user --password your_password --apps monitoramento,imoveis --output-file data.json
        python manage.py migrate_db --source-type sqlite --source-file /path/to/your/database.sqlite3 --apps monitoramento,imoveis --output-file data.json
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-type",
            choices=["mysql", "sqlite", "postgresql"],
            default="mysql",
            help="Source database type",
        )
        parser.add_argument("--host", help="Database host (for MySQL/PostgreSQL)")
        parser.add_argument(
            "--port", type=int, help="Database port (for MySQL/PostgreSQL)"
        )
        parser.add_argument("--database", help="Database name")
        parser.add_argument("--user", help="Database user")
        parser.add_argument("--password", help="Database password")
        parser.add_argument("--source-file", help="SQLite database file path")
        parser.add_argument("--output-file", help="Output fixture file path")
        parser.add_argument(
            "--tables",
            help='Comma-separated list of tables to extract (e.g., "table1,table2")',
        )
        parser.add_argument(
            "--apps",
            help='Comma-separated list of Django apps to extract (e.g., "monitoramento,imoveis")',
        )

    def handle(self, *args, **options):
        if not options["output_file"]:
            self.stdout.write(
                self.style.ERROR("Please specify an output file with --output-file")
            )
            return

        # Connect to source database
        conn = self._connect_to_source_db(options)
        if not conn:
            return

        try:
            # Get all tables
            tables = self._get_tables(conn, options["source_type"])

            # Filter tables if specified
            if options["tables"]:
                # Split by comma or space
                requested_tables = [
                    t.strip() for t in options["tables"].replace(",", " ").split()
                ]
                tables = [t for t in tables if t in requested_tables]
                if not tables:
                    self.stdout.write(
                        self.style.WARNING(
                            f'No matching tables found for: {options["tables"]}'
                        )
                    )
                    return
            elif options["apps"]:
                apps_to_migrate = [app.strip() for app in options["apps"].split(",")]
                tables = self._filter_tables_by_app(tables, apps_to_migrate)
                if not tables:
                    self.stdout.write(
                        self.style.WARNING(
                            f'No matching tables found for apps: {options["apps"]}'
                        )
                    )
                    return

            # Show tables that will be extracted
            self.stdout.write(
                self.style.SUCCESS(f"Will extract data from {len(tables)} tables:")
            )
            for table in tables:
                self.stdout.write(f"  - {table}")

            # Extract data
            self.stdout.write(self.style.SUCCESS("Extracting data..."))
            fixture_data = self._extract_data(conn, tables, options["source_type"])

            # Save to file
            output_path = Path(options["output_file"])
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(fixture_data, f, indent=2, ensure_ascii=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully extracted {len(fixture_data)} records to {output_path}"
                )
            )

        finally:
            conn.close()

    def _connect_to_source_db(self, options):
        try:
            if options["source_type"] == "mysql":
                return pymysql.connect(
                    host=options["host"],
                    port=options["port"] or 3306,
                    user=options["user"],
                    password=options["password"],
                    database=options["database"],
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                )
            elif options["source_type"] == "sqlite":
                return sqlite3.connect(options["source_file"])
            elif options["source_type"] == "postgresql":
                return psycopg2.connect(
                    host=options["host"],
                    port=options["port"] or 5432,
                    database=options["database"],
                    user=options["user"],
                    password=options["password"],
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to connect to database: {str(e)}")
            )
            return None

    def _get_tables(self, conn, source_type):
        cursor = conn.cursor()
        if source_type == "mysql":
            cursor.execute(
                """
                SELECT TABLE_NAME as table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name NOT LIKE 'django_%'
                AND table_name NOT LIKE 'auth_%'
            """
            )
            return [row["table_name"] for row in cursor.fetchall()]
        elif source_type == "sqlite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [
                row[0]
                for row in cursor.fetchall()
                if not row[0].startswith(("django_", "auth_", "sqlite_"))
            ]
        elif source_type == "postgresql":
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name NOT LIKE 'django_%'
                AND table_name NOT LIKE 'auth_%'
            """
            )
            return [row[0] for row in cursor.fetchall()]

    def _filter_tables_by_app(self, tables, apps_to_migrate):
        return [
            table
            for table in tables
            if any(table.startswith(f"{app}_") for app in apps_to_migrate)
        ]

    def _extract_data(self, conn, tables, source_type):
        fixture_data = []
        cursor = conn.cursor()

        for table in tables:
            try:
                # Get table structure
                if source_type == "mysql":
                    cursor.execute(f"DESCRIBE {table}")
                    columns = [row["Field"] for row in cursor.fetchall()]
                elif source_type == "sqlite":
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                elif source_type == "postgresql":
                    cursor.execute(
                        f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                    """,
                        (table,),
                    )
                    columns = [row[0] for row in cursor.fetchall()]

                # Get data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()

                # Convert to fixture format
                for row in rows:
                    if source_type == "mysql":
                        data = dict(row)
                    elif source_type == "sqlite":
                        data = dict(zip(columns, row))
                    elif source_type == "postgresql":
                        data = dict(row)

                    # Convert special types to JSON serializable format
                    for key, value in data.items():
                        if isinstance(value, (datetime.datetime, datetime.date)):
                            data[key] = value.isoformat()
                        elif isinstance(value, decimal.Decimal):
                            data[key] = str(value)

                    fixture_data.append({"model": table, "fields": data})

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Error extracting data from table {table}: {str(e)}"
                    )
                )
                continue

        return fixture_data
