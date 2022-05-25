from os import environ, path
from dotenv import load_dotenv
load_dotenv()


basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))


TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('DB_URL')