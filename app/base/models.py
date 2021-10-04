# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String
from sqlalchemy.sql.sqltypes import Date, PickleType
import time
from app import db, login_manager
import datetime
from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

class Picks(db.Model):

    __tablename__ = 'Picks'

    id = Column(Integer, primary_key=True)
    pick = Column(PickleType)
    direction = Column(String, unique=True)
    bearish = Column(Integer)
    neutral = Column(Integer)
    bullish = Column(Integer)
    total = Column(Integer)
    time= Column(Date, default=datetime.datetime.utcnow())

    #def __init__(self, **kwargs):
        # for property, value in kwargs.items():
        #     if hasattr(value, '__iter__') and not isinstance(value, str):
        #         value = value[0]
        #     if property == 'time':
        #         value = time.ctime() # we need bytes here (not plain str)
        # setattr(self, property, value)
    def __repr__(self):
        return "class picks id is " + str(self.id)