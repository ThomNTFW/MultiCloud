from flask import Blueprint

dynamic_allocation_blueprint = Blueprint('dynamic_allocation_blueprint', __name__)

from . import controller
