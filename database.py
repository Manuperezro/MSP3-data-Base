from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from os import environ, path
from dotenv import load_dotenv
load_dotenv()


basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

current_dir = os.path.dirname(__file__)

database_url = environ.get('DB_URL')

uri = "postgres://ovesfafluvsmiz:1bd280879108710801ffcbe68d1f94e4dba264bf4bd83ab155d87f3b87dc76f5@ec2-176-34-215-248.eu-west-1.compute.amazonaws.com:5432/desl9r7q4mtiq"
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# engine = create_engine(database_url.format(current_dir), convert_unicode=True)

engine = create_engine(uri)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)
    print('We are connected to database succesfully')