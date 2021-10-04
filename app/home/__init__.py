# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Reddit analyzer
"""

from flask import Blueprint

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)
