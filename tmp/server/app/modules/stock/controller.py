from . import stock_blueprint
from flask import jsonify
from .service import get_available_stock, get_current_demand, get_link_costs
import logging

logger = logging.getLogger('waitress')


@stock_blueprint.route("/available_stock", methods=["GET"])
def available_stock():
    try:
        logger.info("Getting available stock and demand...")
        stock = get_available_stock()
        demand = get_current_demand()
        links = get_link_costs()
        return jsonify({"stock": stock, "demand": demand, "links": links})
    except (KeyError, FileNotFoundError):
        logger.error('Issue getting available stock. Please ensure the key for the path for the data files in '
                     'settings.py is present and correct.')
        return jsonify({"message": "Issue getting available stock. "
                                   "Please ensure the key for the path for the data files in settings.py is "
                                   "present and correct."}), 500
