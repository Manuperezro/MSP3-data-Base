from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

current_dir = os.path.dirname(__file__)

database_url = environ.get('DB_URL')

uri = "postgres://kpxglvdutselbp:2e2a2f39c9cc4a6af7ff7becb30ead93e271a478c97fa0b487990d2a1277fc4f@ec2-52-48-159-67.eu-west-1.compute.amazonaws.com:5432/dfmf456hasfnet"
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