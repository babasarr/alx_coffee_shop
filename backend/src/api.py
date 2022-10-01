import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth



app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def retrieve_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_short = [drink.short() for drink in drinks]

    if len(drinks_short) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks_short,
        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
def details_drinks():
    
    if(requires_auth('get:drinks-detail')):    
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_long = [drink.long() for drink in drinks]

        if len(drinks_long) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "drinks": drinks_long,
            }
        )
    else:
        abort(401)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["POST"])
def create_drinks():
    if(requires_auth('post:drinks')):
        body = request.get_json()

        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)

        if new_title is None:
            abort(400)

        try:
            
            drink = Drink(title=new_title, recipe=new_recipe)
            drink.insert()
            drinks_long = drink.long()
            drinks = [drinks_long]

            return jsonify(
                {
                    "success": True,
                    "drinks": drinks,
                }
            )

        except:
            abort(422)
    else:
        abort(401)
        

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
def udate_drink(drink_id):
    if(requires_auth('patch:drinks')):
        body = request.get_json()
        try:
            drink = Drink.query.filter_by(id=drink_id).one_or_none()
            if drink is None:
                abort(404)
            else:
                if 'title' in body:
                    drink.title = body.get('title')
                if 'recipe' in body:
                    drink.recipe = body.get('recipe')

                drink.update()
                drinks_long = drink.long()
                drinks = [drinks_long]

                return jsonify({
                    'success': True,
                    "drinks": drinks,
                })
        except:
            abort(400)
    else:
        abort(401)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(drink_id):
    if(requires_auth('patch:drinks')):
        try:
            drink = Drink.query.filter_by(id=drink_id).one_or_none()
            if drink is None:
                abort(404)
            else:

                drink.delete()

                return jsonify({
                    'success': True,
                    "delete": drink_id
                })
        except:
            abort(400)
    else:
        abort(401)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
            "success": False, 
            "error": 404, 
            "message": "resource not found"
        }),404

@app.errorhandler(401)
def not_found(error):
    return jsonify({
            "success": False, 
            "error": 401, 
            "message": "Unauthorized"
        }),401
    

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, 
        "error": AuthError, 
        "message": "Auth Error"
    }), AuthError

