"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_account(self):
        """It should Read an Account by its identifier"""
        account = self._create_accounts(1)[0]
        response = self.client.get(f"{BASE_URL}/{account.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), account.serialize())

    def test_get_account_not_found(self):
        """It should return 404 when the Account does not exist"""
        response = self.client.get(f"{BASE_URL}/999999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("999999", response.get_json()["message"])

    def test_method_not_allowed(self):
        """It should reject unsupported HTTP methods with 405"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_account_location(self):
        """It should return the new Account URL in the Location header"""
        response = self.client.post(BASE_URL, json=AccountFactory().serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = response.get_json()
        location = response.headers["Location"]
        self.assertTrue(location.endswith(f"{BASE_URL}/{account['id']}"))
        retrieved = self.client.get(location)
        self.assertEqual(retrieved.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieved.get_json(), account)

    def test_update_account(self):
        """It should Update and persist every mutable Account field"""
        account = self._create_accounts(1)[0]
        updated = AccountFactory().serialize()
        updated["id"] = account.id + 1000
        response = self.client.put(f"{BASE_URL}/{account.id}", json=updated)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated["id"] = account.id
        self.assertEqual(response.get_json(), updated)
        db.session.remove()
        self.assertEqual(Account.find(account.id).serialize(), updated)

    def test_update_account_not_found(self):
        """It should not create an Account through PUT"""
        response = self.client.put(f"{BASE_URL}/999999", json=AccountFactory().serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Account.all(), [])

    def test_update_account_invalid_data(self):
        """It should reject invalid updates without modifying persisted data"""
        account = self._create_accounts(1)[0]
        original = account.serialize()
        invalid_payloads = [
            {"name": "Incomplete"},
            [],
            dict(original, name=""),
            dict(original, name=42),
            dict(original, email=None),
            dict(original, address="x" * 257),
            dict(original, phone_number=42),
            dict(original, phone_number="x" * 33),
            dict(original, date_joined="2026-02-30"),
            dict(original, date_joined=42),
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.put(f"{BASE_URL}/{account.id}", json=payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                db.session.remove()
                self.assertEqual(Account.find(account.id).serialize(), original)

    def test_update_account_unsupported_media_type(self):
        """It should require a JSON update document"""
        account = self._create_accounts(1)[0]
        response = self.client.put(f"{BASE_URL}/{account.id}", data="not json")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_account_optional_fields(self):
        """It should allow an omitted phone number and default joining date"""
        account = self._create_accounts(1)[0]
        response = self.client.put(
            f"{BASE_URL}/{account.id}",
            json={"name": "Updated Customer", "email": "customer@example.com", "address": "1 Test Street"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.get_json()["phone_number"])
        self.assertTrue(response.get_json()["date_joined"])
