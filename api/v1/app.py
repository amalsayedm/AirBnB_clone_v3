#!/usr/bin/python3
"""Flask web application
"""

from flask import Flask, jsonify
from flask_cors import CORS
from models import storage
from api.v1.views import app_views
from os

app = Flask(__name__)
app_host = os.getenv('HBNB_API_HOST', '0.0.0.0')
app_port = int(os.getenv('HBNB_API_PORT', '5000'))
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
CORS(app, resources={'/*': {'origins': app_host}})


@app.teardown_appcontext
def teardown(error):
    """Clean-up method
    """
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """Custom 404 error
    """
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(400)
def not_found(error):
    '''Handles the 400 HTTP error code.'''
    msg = 'Bad request'
    if isinstance(error, Exception) and hasattr(error, 'description'):
        msg = error.description
    return jsonify(error=msg), 400


if __name__ == '__main__':
    app_host = os.getenv('HBNB_API_HOST', '0.0.0.0')
    app_port = int(os.getenv('HBNB_API_PORT', '5000'))
    app.run(
        host=app_host,
        port=app_port,
        threaded=True
    )
