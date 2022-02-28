from flask import Blueprint

stock_blueprint = Blueprint('stock_blueprint', __name__)

from . import controller