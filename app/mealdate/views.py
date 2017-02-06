from flask import request, jsonify
from flask import g
from flask import abort
from sqlalchemy import or_, and_


from app import db, auth
from app.utils.rate_limit import ratelimit
from app.utils.json_required import json_required
from app.utils.find_restaurant import find_restaurant
from app.models import MealDate, Proposal, Request
from . import mealdate


@mealdate.route('/api/v1/dates', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_all_dates():
    user = g.user
    dates = MealDate.query.filter(or_(
        MealDate.user_1 == user.id,
        MealDate.user_2 == user.id
        )).all()
    dates = [date.serialize for date in dates]

    return jsonify({'dates': dates}), 200


@mealdate.route('/api/v1/dates', methods=['POST'])
@auth.login_required
@json_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def create_newdate():
    errors = MealDate.validate(request.json)
    if len(errors) == 0:
        proposal_id = request.json.get('proposal_id')
        accept_proposal = request.json.get('accept_proposal')

        proposal = Proposal.query.get_or_404(proposal_id)

        req = proposal.request
        if req.filled:
            return jsonify({'response': False})

        if accept_proposal:
            Proposal.query.filter_by(id=proposal_id).update({'filled': True})
            Request.query.filter_by(id=req.id).update({'filled': True})

            restaurant_name = 'Not found'
            restaurant_address = 'Not found'
            restaurant_picture = 'Not found'

            try:
                restaurant = find_restaurant(req.meal_type, req.location_string)
                if type(restaurant) == dict:
                    restaurant_name = restaurant['name']
                    restaurant_address = restaurant['address']
                    restaurant_picture = restaurant['image_url']
            except Exception as e:
                print e

            date = MealDate(
                user_1=req.user_id,
                user_2=proposal.user_proposed_from,
                restaurant_name=restaurant_name,
                restaurant_address=restaurant_address,
                restaurant_picture=restaurant_picture,
                meal_time=req.meal_time
                )
            db.session.add(date)
            db.session.commit()
            return jsonify({'response': True}), 201
        else:
            db.session.delete(proposal)
            db.session.commit()
            return jsonify({'response': 'Deleted proposal'})
    else:
        return jsonify({'errors': errors}), 400


@mealdate.route('/api/v1/dates/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_date_by_id(id):
    user = g.user
    meal_date = MealDate.query.filter(and_(
        MealDate.id == id,
        or_(user.id == MealDate.user_1, user.id == MealDate.user_2)
        )).first()

    if meal_date is None:
        abort(404)
    return jsonify({'meal_date': meal_date}), 200


@mealdate.route('/api/v1/dates/<int:id>', methods=['PUT'])
@auth.login_required
@json_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def update_date(id):
    old_date = MealDate.query.filter_by(id=id)
    errors = MealDate.validate(request.json)
    if len(errors) == 0:
        proposal_id = request.json.get('proposal_id')
        accept_proposal = request.json.get('accept_proposal')

        proposal = Proposal.query.get_or_404(proposal_id)

        req = proposal.request
        if req.filled:
            return jsonify({'response': False})
        if accept_proposal:
            proposal.update({'filled': True})
            req.update({'filled': True})

            restaurant_name = ''
            restaurant_address = ''
            restaurant_picture = ''

            try:
                restaurant = find_restaurant(req.meal_type, req.location_string)
                if type(restaurant) == dict:
                    restaurant_name = restaurant['name']
                    restaurant_address = restaurant['address']
                    restaurant_picture = restaurant['image_url']
            except Exception as e:
                print e

            date = MealDate(
                user_1=req.user_id,
                user_2=proposal.user_proposed_from,
                restaurant_name=restaurant_name,
                restaurant_address=restaurant_address,
                restaurant_picture=restaurant_picture,
                meal_time=req.meal_time
            )
            old_date.update(date)
            db.session.commit()
            return jsonify({'response': True}), 201
        else:
            db.session.delete(proposal)
            db.session.commit()
            return jsonify({'response': 'Deleted proposal'})
    else:
        return jsonify({'errors': errors}), 400


@mealdate.route('/api/v1/dates/<int:id>', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def delete_date(id):
    user = g.user
    meal_date = MealDate.query.filter(and_(
        MealDate.id == id,
        or_(user.id == MealDate.user_1, user.id == MealDate.user_2)
        )).first()

    if meal_date is None:
        abort(400)

    db.session.delete(meal_date)
    db.session.commit()

    return jsonify({'response': True})

