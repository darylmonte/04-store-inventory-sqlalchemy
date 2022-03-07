from sqlalchemy import (create_engine, 
                        Column, Integer, String, Date)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# create a database - books.db
engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# create a model
class Product(Base):
    __tablename__ = 'products'

# title, author, date published, price
    product_id = Column(Integer, primary_key=True)
    product_name = Column('Product Name', String)
    product_price = Column('Price', Integer)
    product_quantity = Column('Quantity', Integer)
    date_updated = Column('Date Updated', Date)

    def __repr__(self):
        return f'Product Name: {self.product_name} Price: {self.product_price} Quantity: {self.product_quantity} Date Updated: {self.date_updated} '