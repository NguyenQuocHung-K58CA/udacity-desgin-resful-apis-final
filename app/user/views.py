from flask import request, jsonify
from flask import g
from flask import abort


from app import db, auth
from app.utils.rate_limit import ratelimit
from app.utils.json_required import json_required
from app.models import User
from . import user
from .forms import UserSchema


@user.route('/api/v1/token', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')}), 200


@user.route('/api/v1/users', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_users():
    users = User.query.all()
    users = [user.serialize for user in users]
    return jsonify({'users': users}), 200


@user.route('/api/v1/users/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def get_user_profile(id):
    user = User.query.get_or_404(id)
    if not user:
        abort(400)
    return jsonify({'user': user.serialize}), 200


@user.route('/api/v1/users', methods=['POST'])
@ratelimit(limit=180, per=60*1)
@json_required
def create_new_user():
    errors = UserSchema().load(request.json).errors
    print errors
    if len(errors):
        return jsonify({'errors': errors})

    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({'user': user.serialize, 'message': 'user already exist.'})

    user = User(username=username)
    user.hash_password(password)

    db.session.add(user)
    db.session.commit()
    return jsonify({'user': user.serialize}), 201


@user.route('/api/v1/users', methods=['PUT'])
@auth.login_required
@json_required
@ratelimit(limit=180, per=60*1, scope_func=lambda: g.user.id)
def update_user():
    user = g.user
    user = User.query.get_or_404(user.id)

    errors = UserSchema().load(request.json).errors
    if len(errors):
        return jsonify({'errors': errors})

    username = request.json.get('username')
    email = request.json.get('password')
    picture = request.json.get('picture')

    if not picture:
        picture = 'default.jpg'
    new_user = {
        'username': username,
        'email': email,
        'picture': picture
    }

    user.update(new_user)

    db.session.commit()

    return jsonify({'user': user.first().serialize}), 200
