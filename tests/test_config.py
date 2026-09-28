"""Verify database configuration without changing the running application's config."""
import os
import runpy
from unittest import TestCase
from unittest.mock import patch
from service import config


class TestConfiguration(TestCase):
    """Application configuration tests."""

    def load_config(self, environment):
        """Execute configuration in a fresh namespace with isolated test inputs."""
        with patch.dict(os.environ, environment, clear=True):
            return runpy.run_path(config.__file__)

    def test_explicit_database_uri(self):
        """It should prefer an explicit database URI over component defaults."""
        uri = "postgresql://test-user:test-password@database:5432/testdb"
        result = self.load_config({"DATABASE_URI": uri})
        self.assertEqual(result["SQLALCHEMY_DATABASE_URI"], uri)
        self.assertFalse(result["SQLALCHEMY_TRACK_MODIFICATIONS"])

    def test_database_components(self):
        """It should assemble the database URI from environment components."""
        result = self.load_config({
            "DATABASE_USER": "test-user",
            "DATABASE_PASSWORD": "test-password",
            "DATABASE_HOST": "database",
            "DATABASE_NAME": "testdb",
            "SECRET_KEY": "isolated-test-value",
        })
        self.assertEqual(
            result["SQLALCHEMY_DATABASE_URI"],
            "postgresql://test-user:test-password@database:5432/testdb",
        )
        self.assertEqual(result["SECRET_KEY"], "isolated-test-value")

    def test_lab_database_defaults(self):
        """It should retain the starter's local lab database defaults."""
        result = self.load_config({})
        self.assertEqual(
            result["SQLALCHEMY_DATABASE_URI"],
            "postgresql://postgres:postgres@localhost:5432/postgres",
        )
