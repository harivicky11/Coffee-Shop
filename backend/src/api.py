import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# ROUTES


'''
Public route for getting all drinks
'''
@app.route('/drinks')
def get_drinks():
    # get all drinks
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .short()
    drinks_short = [drink.short() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })

# Error Handling


'''
Error handling for resource not found
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
