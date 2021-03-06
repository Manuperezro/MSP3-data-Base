from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from sqlalchemy.orm import relationship
import uuid
import datetime


class Recipes(Base):
    __tablename__ = 'recipes'
    id = Column(String(1000), primary_key=True)
    user_id = Column(String(1000))
    name = Column(String(1000))
    description = Column(String(1000), nullable=True)
    site_url = Column(String(500), nullable=True)
    draw = Column(Integer(), default=0)
    created_time = Column(DateTime(), nullable=False)
    modified_time = Column(DateTime(), nullable=False)


    def __init__(self, name, description, site_url, user_id):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.name = name
        self.description = description
        self.site_url = site_url
        self.created_time = datetime.datetime.now()
        self.modified_time = datetime.datetime.now()

    def __repr__(self):
        return '<Recipe %r>' % (self.user_id)