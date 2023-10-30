#!/usr/bin/python3
'''Contains the places view for the API.'''
from flask import abort, jsonify, make_response, request
import requests
from api.v1.views import app_views
from api.v1.views.amenities import amenities
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
import json
from os import getenv


@app_views.route('cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def place(city_id):
    """Retrieves all Place objects of aspecifiec City"""
    obj_city = storage.get(City, city_id)
    if not obj_city:
        abort(404)

    return jsonify([obj.to_dict() for obj in obj_city.places])


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def single_place(place_id):
    """Retrieves a Place object"""
    obj = storage.get(Place, place_id)
    if not obj:
        abort(404)
    return jsonify(obj.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def del_place(place_id):
    """Returns an empty dictionary with the status code 200"""
    obj = storage.get(Place, place_id)
    if not obj:
        abort(404)
    obj.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def post_place(city_id):
    """Returns the new Place with the status code 201"""
    obj_city = storage.get(City, city_id)
    if not obj_city:
        abort(404)

    newplace = request.get_json()
    if not newplace:
        abort(400, 'Not a JSON')
    if 'user_id' not in newplace:
        abort(400, "Missing user_id")
    user_id = newplace['user_id']
    obj_user = storage.get(User, user_id)
    if not obj_user:
        abort(404)
    if 'name' not in newplace:
        abort(400, "Missing name")

    obj = Place(**newplace)
    setattr(obj, 'city_id', city_id)
    storage.new(obj)
    storage.save()
    return make_response(jsonify(obj.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def put_place(place_id):
    """Returns the Place object with the status code 200"""
    obj = storage.get(Place, place_id)
    if not obj:
        abort(404)

    req = request.get_json()
    if not req:
        abort(400, "Not a JSON")

    for k, v in req.items():
        if k not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(obj, k, v)

    storage.save()
    return make_response(jsonify(obj.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Search for place according to parameters
    in body request
    """
    # POST REQUEST
    if request.is_json:  # check is request is valid json
        body = request.get_json()
    else:
        abort(400, 'Not a JSON')

    place_list = []

    # if states searched
    if 'states' in body:
        for state_id in body['states']:
            state = storage.get(State, state_id)
            if state is not None:
                for city in state.cities:
                    for place in city.places:
                        place_list.append(place)

    # if cities searched
    if 'cities' in body:
        for city_id in body['cities']:
            city = storage.get(City, city_id)
            if city is not None:
                for place in city.places:
                    place_list.append(place)

    # if 'amenities' present
    if 'amenities' in body and len(body['amenities']) > 0:
        if len(place_list) == 0:
            place_list = [place for place in storage.all(Place).values()]
        del_list = []
        for place in place_list:
            for amenity_id in body['amenities']:
                amenity = storage.get(Amenity, amenity_id)
                if amenity not in place.amenities:
                    del_list.append(place)
                    break
        for place in del_list:
            place_list.remove(place)

    if len(place_list) == 0:
        place_list = [place for place in storage.all(Place).values()]

    # convert objs to dict and remove 'amenities' key
    place_list = [place.to_dict() for place in place_list]
    for place in place_list:
        try:
            del place['amenities']
        except KeyError:
            pass

    return jsonify(place_list)
