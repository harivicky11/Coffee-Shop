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


'''
Route handler for getting detailed representation of all drinks.
Requires 'get:drinks-detail' permission.
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # get all drinks and format using .long()
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .long()
    drinks_long = [drink.long() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_long
    })


'''
Route handler for adding new drink.
Requires 'post:drinks' permission.
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get the drink info from request
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    # create a new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        # add drink to the database
        drink.insert()
    except Exception as e:
        print('ERROR: ', str(e))
        abort(422)

    return jsonify({
        "success": True,
        "drinks": drink.long()
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
