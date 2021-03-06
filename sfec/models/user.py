# -*- coding: utf-8 -*-

from datetime import datetime
from hashlib import sha512

from flask import request
from storm.expr import And
from storm.properties import DateTime, Unicode
from storm.references import Reference

from sfec.database.runtime import get_default_store
from sfec.models.base import BaseModel


class User(BaseModel):

    __storm_table__ = "sfec_user"

    name = Unicode()

    # Basic login data
    email = Unicode()
    password = Unicode()

    birth_date = DateTime()
    register_date = DateTime()

    def __init__(self):
        self.register_date = datetime.now()

    #
    # Properties
    #

    @property
    def is_admin(self):
        store = get_default_store()
        return store.find(Admin, id=self.id).one() is not None

    #
    # Static API
    #

    @staticmethod
    def hash(password):
        """The hash function to be used by the table"""
        return unicode(sha512(password).hexdigest())

    @classmethod
    def authenticate(cls, store, email, password):
        """Returns the user that matches the email password combination"""
        pw_hash = cls.hash(password)
        queries = [cls.email == email, cls.password == pw_hash]

        user = store.find(cls, And(*queries)).one()
        if user:
            user.last_login = datetime.now()
            user.last_ip = unicode(request.remote_addr)
            store.commit()
            return user

        return False

    #
    # Public API
    #

    def dict(self):
        super_dict = super(User, self).dict()
        super_dict['is_admin'] = self.is_admin
        return super_dict

    def set_password(self, password):
        self.password = self.hash(password)


class Admin(BaseModel):

    __storm_table__ = "sfec_admin"

    user = Reference('Admin.id', 'User.id')


class Vendor(BaseModel):

    __storm_table__ = "sfec_vendor"

    user = Reference('Vendor.id', 'User.id')


class Customer(BaseModel):

    __storm_table__ = "sfec_customer"

    user = Reference('Customer.id', 'User.id')
