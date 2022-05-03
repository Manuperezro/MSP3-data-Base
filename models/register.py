from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime


db = SQLAlchemy()

class User(Base):
    __tablename__= "users" 
    id =  Column(Integer(), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = db.Column(String(), nullable=False)

