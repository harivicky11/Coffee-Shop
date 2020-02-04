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


'''
Route handler for editing existing drink.
Requires 'patch:drinks' permission.
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_by_id(*args, **kwargs):
    # get id from kwargs
    id = kwargs['id']

    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    # get request body
    body = request.get_json()

    # update title if present in body
    if 'title' in body:
        drink.title = body['title']

    # update recipe if present in body
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        # update drink in database
        drink.insert()
    except Exception as e:
        # catch exceptions
        print('EXCEPTION: ', str(e))

        # Bad Request
        abort(400)

    # array containing .long() representation
    drink = [drink.long()]

    # return drink to view
    return jsonify({
        'success': True,
        'drinks': drink
    })


'''
Route handler for deleting drink.
Requires 'delete:drinks' permission.
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    # get id from kwargs
    id = kwargs['id']

    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    try:
        # delete drink from database
        drink.delete()
    except Exception as e:
        # catch exceptions
        print('EXCEPTION: ', str(e))

        # server error
        abort(500)

    # return status and deleted drink id
    return jsonify({
        'success': True,
        'delete': id
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


'''
Error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
Error handling for bad request
'''
@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
Error handling for AuthError
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
