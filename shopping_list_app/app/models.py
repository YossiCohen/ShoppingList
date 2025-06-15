from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

# Assuming db instance is created in extensions.py and imported here
from .extensions import db
# For now, to make this file parsable without extensions.py, we'll define a placeholder.
# This will be replaced by the actual db object when extensions.py is created.
# from flask_sqlalchemy import SQLAlchemy # No longer needed here
# db = SQLAlchemy() # No longer needed here

# Association table for User and Household many-to-many relationship
user_households = Table('user_households', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('household_id', Integer, ForeignKey('households.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

    households = relationship('Household', secondary=user_households,
                              back_populates='users', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login required methods are inherited from UserMixin:
    # is_authenticated, is_active, is_anonymous, get_id()
    # get_id() is provided by UserMixin and uses the primary key `id`.

    def __repr__(self):
        return f'<User {self.username}>'

class Household(db.Model):
    __tablename__ = 'households'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    users = relationship('User', secondary=user_households,
                         back_populates='households', lazy='dynamic')

    shopping_lists = relationship('ShoppingList', back_populates='household', lazy='dynamic',
                                  cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Household {self.name}>'

class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default='Unnamed List') # Added name attribute
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)

    household = relationship('Household', back_populates='shopping_lists')
    items = relationship('ShoppingItem', back_populates='shopping_list', lazy='dynamic',
                         cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ShoppingList id={self.id} date={self.date}>'

class ShoppingItem(db.Model):
    __tablename__ = 'shopping_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    amount = Column(String(50), nullable=True)
    free_text = Column(Text, nullable=True)
    bought = Column(db.Boolean, default=False, nullable=False) # Added bought status
    shopping_list_id = Column(Integer, ForeignKey('shopping_lists.id'), nullable=False)

    shopping_list = relationship('ShoppingList', back_populates='items')

    def __repr__(self):
        return f'<ShoppingItem {self.name}>'
