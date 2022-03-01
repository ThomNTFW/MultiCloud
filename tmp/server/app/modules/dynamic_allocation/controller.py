from . import dynamic_allocation_blueprint
from .service import trigger_optimization_service
from flask import request, jsonify
import logging

logger = logging.getLogger('waitress')


@dynamic_allocation_blueprint.route("/trigger_optimization", methods=["POST"])
def trigger_optimization():
    logger.info(f'Triggering optimization...')
    data = request.json

    if not data:
        logger.error("Please supply valid json body with request.")
        return "Please supply valid json body with request.", 422

    if "sku_source_ids" not in data:
        logger.error("Please supply the following required variables in the body of your request: 'sku_source_ids'")
        return jsonify({"message": "Please supply the following required variables in the body "
                                   "of your request: 'sku_source_ids'"}), 422

    if not data["sku_source_ids"]:
        logger.error("Please supply at least one sku_source for the optimization.")
        return jsonify({"message": "Please supply at least one sku_source for the optimization."}), 422

    if "margin" in data:
        if not isinstance(data["margin"], (int, float)) or data["margin"] < 0 or data["margin"] > 1:
            logger.error("Please supply a number between 0 and 1 for the margin.")
            return jsonify({"message": "Please supply a number between 0 and 1 for the margin."}), 422

    logger.info(f'The following sku_sources will be considered for the dynamic allocation: {data["sku_source_ids"]}')

    if "margin" in data:
        logger.info(f'Using a margin of {data["margin"]}')
        optimization_result, status_code = trigger_optimization_service(data["sku_source_ids"], data["margin"])
    else:
        optimization_result, status_code = trigger_optimization_service(data["sku_source_ids"])

    return jsonify(optimization_result), status_code
