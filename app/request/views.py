from flask import request, jsonify
from flask import g
from flask import abort
from sqlalchemy import and_


from app import db, auth
from app.utils.rate_limit import ratelimit
from app.models import Request
from . import request as request_api


@request_api.route('/api/v1/requests', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_all_requests():
    user = g.user
    requests = Request.query.filter(user.id != Request.user_id).all()
    requests = [req.serialize for req in requests]
    return jsonify({'requests' : requests})


@request_api.route('/api/v1/requests', methods=['POST'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def create_new_request():
    errors = Request.validate(request.json)
    if len(errors)==0:
        user = g.user
        meal_type = request.json.get('meal_type')
        location_string = request.json.get('location_string')
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')
        meal_time = request.json.get('meal_time')

        req = Request(meal_type=meal_type, meal_time=meal_time,
                      location_string=location_string, user_id=user.id,
                      latitude=latitude, longitude=longitude)

        db.session.add(req)
        db.session.commit()
        return jsonify({'result': True}), 201
    else:
        return jsonify({'errors': errors})


@request_api.route('/api/v1/requests/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_request_by_id(id):
    req = Request.query.get_or_404(id)
    if not req:
        abort(400)
    else:
        return jsonify({'request': req.serialize}), 200


@request_api.route('/api/v1/requests/<int:id>', methods=['PUT'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def update_request(id):
    user = g.user
    req = Request.query.filter(and_(Request.id == id, user.id == Request.user_id))
    if not req:
        abort(400)

    errors = Request.validate(request.json)
    if len(errors)==0:
        meal_type = request.json.get('meal_type')
        location_string = request.json.get('location_string')
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')
        meal_time = request.json.get('meal_time')
        new_req = {
            'meal_type': meal_type,
            'meal_time': meal_time,
            'latitude' : latitude,
            'longitude': longitude,
            'location_string': location_string
        }

        req.update(new_req)
        db.session.commit()
        return jsonify({'response': True})
    else:
        return jsonify({'errors': errors})


@request_api.route('/api/v1/requests/<int:id>', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def delete_request(id):
    user = g.user
    req = Request.query.filter(and_(Request.id == id, user.id == Request.user_id)).first()

    if not req:
        abort(400)

    db.session.delete(req)
    db.session.commit()
    return jsonify({'response': True})

