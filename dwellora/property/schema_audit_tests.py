from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class SchemaAuditCommandTests(TestCase):
    def test_schema_audit_is_read_only_and_reports_registered_tables(self):
        output = StringIO()
        call_command("audit_dwellora_schema", stdout=output)
        result = output.getvalue()
        self.assertIn("READ ONLY", result)
        self.assertIn("Model table inventory", result)
        self.assertIn("property_listing", result)
        self.assertIn("Migration state", result)
        self.assertIn("Existing tables not mapped", result)
        self.assertIn("No migration conflicts detected", result)
