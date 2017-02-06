from functools import wraps
from flask import request, jsonify


def json_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.json is None:
            message = {'error': 'data must be json'}
            return jsonify(message), 400

        return f(*args, **kwargs)
    return wrapper