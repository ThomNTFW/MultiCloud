from flask import Flask
from app.modules.dynamic_allocation import dynamic_allocation_blueprint
from app.modules.stock import stock_blueprint
from werkzeug.utils import import_string
import logging

logging.basicConfig()
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)


def create_app(name=__name__, environment=None):
    if environment == "prod":
        env_settings = 'ProdConfig'
    elif environment == "test":
        env_settings = 'TestConfig'
    elif environment == "dev":
        env_settings = 'DevConfig'
    else:
        logger.warning("No value found for Environment, defaulting to dev...")
        env_settings = 'DevConfig'

    logger.info(f'Environment set to "{environment}". Using config "{env_settings}"')

    flask_app = Flask(__name__)
    load_config(flask_app, env_settings)
    register_blueprints(flask_app)
    return flask_app


def load_config(flask_app, env_settings):
    logger.info('Setting configs...')
    config = import_string(f'settings.{env_settings}')
    flask_app.config.from_object(config)


def register_blueprints(flask_app):
    logger.info('Registering blueprints...')
    flask_app.register_blueprint(dynamic_allocation_blueprint, url_prefix='/api')
    flask_app.register_blueprint(stock_blueprint, url_prefix='/api')

