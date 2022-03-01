
from app import create_app
from waitress import serve

app = create_app(environment="dev")

if app.config['DEBUG']:
    app.debug = True

serve(app, host=app.config['DEFAULT_HOST'], port=app.config["DEFAULT_PORT"])
