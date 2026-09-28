"""
Models for Account

All of the models are stored in this module
"""
import logging
from datetime import date
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Account.init_db(app)


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  A C C O U N T   M O D E L
######################################################################
class Account(db.Model, PersistentBase):
    """
    Class that represents an Account
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(32), nullable=True)  # phone number is optional
    date_joined = db.Column(db.Date(), nullable=False, default=date.today)

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Account into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat()
        }

    def deserialize(self, data):
        """
        Deserializes a Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        if not isinstance(data, dict):
            raise DataValidationError("Invalid Account: a JSON object is required")

        values = {}
        for field, maximum in (("name", 64), ("email", 64), ("address", 256)):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise DataValidationError(
                    f"Invalid Account: {field} must be nonempty text of at most {maximum} characters"
                )
            values[field] = value

        phone_number = data.get("phone_number")
        if phone_number is not None and (
            not isinstance(phone_number, str) or len(phone_number) > 32
        ):
            raise DataValidationError("Invalid Account: phone_number must be text of at most 32 characters")
        try:
            joined = data.get("date_joined")
            joined = date.today() if joined is None else date.fromisoformat(joined)
        except (TypeError, ValueError) as error:
            raise DataValidationError("Invalid Account: date_joined must use YYYY-MM-DD") from error

        # Validate the entire document before mutating a persistent account.
        self.name = values["name"]
        self.email = values["email"]
        self.address = values["address"]
        self.phone_number = phone_number
        self.date_joined = joined
        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Accounts with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
