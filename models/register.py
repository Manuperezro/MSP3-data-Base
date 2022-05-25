from sqlalchemy import Column, Integer, String, DateTime, JSON 
from sqlalchemy.dialects import postgresql
from database import Base
from sqlalchemy.orm import relationship
import uuid
import datetime

class Users(Base):

    __tablename__= "users" 
    id = Column(String(50), primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(), nullable=False)
    created_time = Column(DateTime(), nullable=False)
 

    def __init__(self, username, password, email):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password
        self.created_time = datetime.datetime.now()


    def __repr__(self):
        return '<Register %r>' % (self.username)

