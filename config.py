from os import environ, path
from dotenv import load_dotenv
load_dotenv()


TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
