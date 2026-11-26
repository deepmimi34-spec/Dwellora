from collections import defaultdict

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Read-only inventory of Django model tables, existing database tables, and migration history."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            existing = set(connection.introspection.table_names(cursor))
            migration_table = "django_migrations" in existing
            migrations = []
            if migration_table:
                cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
                migrations = cursor.fetchall()

        model_tables = defaultdict(list)
        for model in apps.get_models(include_auto_created=False):
            if model._meta.proxy or model._meta.abstract:
                continue
            model_tables[model._meta.db_table].append(f"{model._meta.app_label}.{model.__name__}")

        self.stdout.write(self.style.MIGRATE_HEADING("Dwellora schema inventory (READ ONLY)"))
        self.stdout.write(f"Database vendor: {connection.vendor}")
        self.stdout.write(f"Existing tables: {len(existing)}")
        self.stdout.write("Migration history table: django_migrations")
        self.stdout.write(f"Migration history table exists: {migration_table}")
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Model table inventory"))
        missing = []
        collisions = []
        for table, models_for_table in sorted(model_tables.items()):
            if len(models_for_table) > 1:
                collisions.append((table, models_for_table))
            state = "PRESENT" if table in existing else "MISSING"
            if state == "MISSING":
                missing.append(table)
            self.stdout.write(f"{state:7} {table}: {', '.join(models_for_table)}")

        if collisions:
            self.stdout.write(self.style.ERROR("\nModel table-name collisions:"))
            for table, models_for_table in collisions:
                self.stdout.write(f"  {table}: {', '.join(models_for_table)}")
        else:
            self.stdout.write(self.style.SUCCESS("\nNo duplicate model table names detected."))

        if missing:
            self.stdout.write(self.style.WARNING("\nModel tables missing from database:"))
            for table in missing:
                self.stdout.write(f"  {table}")
        else:
            self.stdout.write(self.style.SUCCESS("\nAll registered model tables exist."))

        if migration_table:
            self.stdout.write(self.style.MIGRATE_HEADING("\nMigration history"))
            self.stdout.write(f"Recorded migration rows: {len(migrations)}")
            for app, name in migrations:
                self.stdout.write(f"  {app}: {name}")
        else:
            self.stdout.write(self.style.WARNING("\nNo django_migrations table found. Migration history is not established."))

        self.stdout.write(self.style.WARNING(
            "\nThis command did not read property/user records or modify the database. "
            "Do not apply migrations until this report is reviewed against a backup."
        ))
