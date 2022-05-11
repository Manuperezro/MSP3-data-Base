from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from sqlalchemy.orm import relationship
import uuid
import datetime


class Recipes(Base):
    __tablename__ = 'recipes'
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    description = Column(String(100), nullable=True)
    site_url = Column(String(200), nullable=True)
    draw = Column(Integer(), default=0)
    created_time = Column(DateTime(), nullable=False)
    modified_time = Column(DateTime(), nullable=False)
    histories = relationship(
        'Histories',
        backref='recipes',
        cascade='all,delete'
    )

    def __init__(self, name, description, site_url):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.site_url = site_url
        self.created_time = datetime.datetime.now()
        self.modified_time = datetime.datetime.now()
      

    def __repr__(self):
        return '<Recipe %r>' % (self.name)