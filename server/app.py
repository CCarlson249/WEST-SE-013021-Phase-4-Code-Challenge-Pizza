#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api

from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def restaurants():
    restaurants= Restaurant.query.all()
    restaurants_dictionary = [restaurant.to_dict() for restaurant in restaurants]
    
    response = make_response(
        jsonify(restaurants_dictionary),
        200
    )

    return response

@app.route('/restaurant/<int:id>', methods = ['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if not restaurant:
        response = make_response(
            {'error': 'Restaurant not found'},
            404
        )
        return response

    if request.method == 'GET':
        restaurant_dictionary = restaurant.to_dict(rules=('pizzas',))
        response = make_response(
            jsonify(restaurant_dictionary),
            200
        )

    elif request.method == 'DELETE':
        RestaurantPizza.query.filter(RestaurantPizza.restaurant_id == id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        response = make_response({'success': 'DELETED'}, 200)

    return response

@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = Pizza.query.all()
    pizzas_dictionary = [pizza.to_dict() for pizza in pizzas]

    response = make_response(
        jsonify(pizzas_dictionary),
        200
    )

    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    try: 
        new_pizza = RestaurantPizza(
            price=request.get_json()['price'],
            restaurant_id=request.get_json()['restaurant_id'],
            pizza_id=request.get_json()['pizza_id']
        )
        db.session.add(new_pizza)
        db.session.commit()

        pizza_dictionary = new_pizza.pizza.to_dict(rules=('-restaurant_pizzas',))

        return make_response(jsonify(pizza_dictionary), 201)

    except ValueError as e:  
        return make_response({"errors": [str(e)]}, 400)  

if __name__ == '__main__':
    app.run(port=5555, debug=True)
