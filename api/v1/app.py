#!/usr/bin/python3
"""
Flask web application
"""

from flask import Flask, jsonify
from models import storage
from api.v1.views import app_views
from os import getenv
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_views)
app_host = getenv('HBNB_API_HOST', '0.0.0.0')
app_port = int(getenv('HBNB_API_PORT', '5000'))
app.url_map.strict_slashes = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app, resources={'/*': {'origins': app_host}})


@app.teardown_appcontext
def teardown(error):
    """
    Clean-up method
    """
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 error
    """
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(host=getenv('HBNB_API_HOST', '0.0.0.0'),
            port=getenv('HBNB_API_PORT', '5000'),
            threaded=True)
