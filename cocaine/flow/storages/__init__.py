# -*- coding: utf-8 -*-
from __future__ import absolute_import
from werkzeug.local import LocalProxy
from flask import current_app

class ST(object):
    
    @staticmethod
    def instance():
        return ST._instance

def connect_to_database(app):
    if app.config['STORAGE'] == 'elliptics':
        from .elliptics import Elliptics
        rez = Elliptics(app.config['ELLIPTICS_NODES'], app.config['ELLIPTICS_GROUPS'])
        ST._instance = rez
        return rez
    elif app.config['STORAGE'] == 'mongo':
        from .mongo import Mongo
        return Mongo(app)
    raise ValueError('Unsupported type of storage')


def get_storage():
    return current_app.storage


def init_storage(app):
    app.storage = connect_to_database(app)


storage = LocalProxy(get_storage)

