from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Create an instance of the Flask class.
app = Flask(__name__)

# Configure our app with a secret key from the config class
app.config.from_object(Config)

# Create an instance of SQLAlchemy to represent our database
db = SQLAlchemy(app)

# Create an instance of Migrate to handle the database migrations of our flask app
migrate = Migrate(app, db)

# Create an instance of LoginManager to handle authentication
login = LoginManager(app)

# Customize login process - if not logged in, redirect to login page
login.login_view = 'login'
login.login_message = 'You need to be logged in to do that.'
login.login_message_category = 'danger'

# Register the api blueprint with our app
from app.blueprints.api import api
app.register_blueprint(api)

# import all of the routes from the routes file inot the current package
from app import routes, models