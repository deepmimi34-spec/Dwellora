from collections import defaultdict

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.loader import MigrationLoader


class Command(BaseCommand):
    help = (
        "Read-only inventory of model tables, database tables, migration history, "
        "unapplied migrations, and migration conflicts."
    )

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            existing = set(connection.introspection.table_names(cursor))

        migration_table = "django_migrations" in existing
        loader = MigrationLoader(connection, ignore_no_migrations=True)
        applied = set(loader.applied_migrations)
        leaves = set(loader.graph.leaf_nodes())
        unapplied = sorted(leaves - applied)
        conflicts = loader.detect_conflicts()

        model_tables = defaultdict(list)
        for model in apps.get_models(include_auto_created=True):
            if model._meta.proxy or model._meta.abstract:
                continue
            model_tables[model._meta.db_table].append(
                f"{model._meta.app_label}.{model.__name__}"
            )

        expected_tables = set(model_tables)
        missing = sorted(expected_tables - existing)
        extra = sorted(existing - expected_tables)
        collisions = [
            (table, model_names)
            for table, model_names in sorted(model_tables.items())
            if len(model_names) > 1
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("Dwellora schema inventory (READ ONLY)"))
        self.stdout.write(f"Database vendor: {connection.vendor}")
        self.stdout.write(f"Existing tables: {len(existing)}")
        self.stdout.write(f"Expected model tables: {len(expected_tables)}")
        self.stdout.write(f"Migration history table exists: {migration_table}")
        self.stdout.write("")

        self.stdout.write(self.style.MIGRATE_HEADING("Model table inventory"))
        for table, model_names in sorted(model_tables.items()):
            state = "PRESENT" if table in existing else "MISSING"
            self.stdout.write(f"{state:7} {table}: {', '.join(model_names)}")

        if collisions:
            self.stdout.write(self.style.ERROR("\nModel table-name collisions:"))
            for table, model_names in collisions:
                self.stdout.write(f"  {table}: {', '.join(model_names)}")
        else:
            self.stdout.write(self.style.SUCCESS("\nNo duplicate model table names detected."))

        if missing:
            self.stdout.write(self.style.WARNING("\nExpected model tables missing from database:"))
            for table in missing:
                self.stdout.write(f"  {table}")
        else:
            self.stdout.write(self.style.SUCCESS("\nAll expected model tables are present."))

        self.stdout.write(self.style.MIGRATE_HEADING("\nExisting tables not mapped to registered Django models"))
        if extra:
            for table in sorted(extra):
                self.stdout.write(f"  {table}")
            self.stdout.write(
                self.style.WARNING(
                    "Review these tables: they may be legacy, unmanaged, third-party, "
                    "or intentionally created outside Django."
                )
            )
        else:
            self.stdout.write("  None detected.")

        self.stdout.write(self.style.MIGRATE_HEADING("\nMigration state"))
        self.stdout.write(f"Applied migration records: {len(applied)}")
        self.stdout.write(f"Unapplied leaf migrations: {len(unapplied)}")
        if unapplied:
            for app_label, migration_name in unapplied:
                self.stdout.write(f"  PENDING {app_label}: {migration_name}")
        else:
            self.stdout.write(self.style.SUCCESS("No unapplied leaf migrations detected."))

        if conflicts:
            self.stdout.write(self.style.ERROR("\nMigration conflicts detected:"))
            for app_label, migration_names in sorted(conflicts.items()):
                self.stdout.write(f"  {app_label}: {', '.join(migration_names)}")
        else:
            self.stdout.write(self.style.SUCCESS("\nNo migration conflicts detected."))

        if not migration_table:
            self.stdout.write(self.style.WARNING(
                "\nNo django_migrations table found. Migration history is not established."
            ))

        self.stdout.write(self.style.WARNING(
            "\nREAD-ONLY AUDIT: no property/user records were queried and no schema or data "
            "was changed. Table names alone do not establish data safety. Review this report, "
            "confirm the database target, and take a verified backup before migration planning."
        ))
