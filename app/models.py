from app import db

import random, string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

secret_key = ''.join(random.choice(string.letters + string.digits) for idx in range(32))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True)
    picture = db.Column(db.String(512))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)

        try:
            data = s.loads(token)
        except SignatureExpired:
            print 'token expired.'
            return None
        except BadSignature:
            print 'invaild token'
            return None

        user_id = data['id']
        return user_id

    @staticmethod
    def validate(item):
        required_fields = ['username', 'password', 'email']
        errors = []

        if type(item) != dict:
            errors.append({'error': "item must be a dict"})
        else:
            for key in required_fields:
                if not key in item:
                    error = {key: 'required'}
                    errors.append(error)
                elif not item[key]:
                    error = {key: 'required'}
                    errors.append(error)

        return errors

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture,
        }


class Request(db.Model):
    """ doc string """
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    meal_type = db.Column(db.String(128))
    location_string = db.Column(db.String(128))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    meal_time = db.Column(db.String(64))
    filled = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id, innerjoin=True, lazy='joined')

    @staticmethod
    def validate(item):
        errors = []
        required_fields = ['meal_type', 'location_string', 'longitude', 'latitude', 'meal_time']
        if type(item) == dict:
            for key in required_fields:
                if not key in item:
                    errors.append({key: 'required'})
                elif not item[key]:
                    errors.append({key: 'required'})
        else:
            errors.append({"error": 'item must be a dict'})

        return errors

    @property
    def serialize(self):
        return {
            'id': self.id,
            'meal_type': self.meal_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'meal_time': self.meal_time,
            'location_string': self.location_string,
            'filled': self.filled
        }


class Proposal(db.Model):
    __tablename__ = 'proposal'
    id = db.Column(db.Integer, primary_key=True)
    user_proposed_to = db.Column(db.Integer)
    user_proposed_from = db.Column(db.Integer)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    filled = db.Column(db.Boolean, default=False)
    request = db.relationship('Request', foreign_keys=request_id, innerjoin=True, lazy='joined')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'user_proposed_to': self.user_proposed_to,
            'user_proposed_from': self.user_proposed_from,
            'filled': self.filled
        }

    @staticmethod
    def validate(item):
        required_fields = ['request_id']
        errors = []

        if type(item) == dict:
            for key in required_fields:
                if not key in required_fields:
                    errors.append({key: 'required'})
                elif not item[key]:
                    errors.append({key: 'required'})
        else:
            errors.append({"error": 'item must be a dict'})

        return errors


class MealDate(db.Model):
    __tablename__ = "mealdate"
    id = db.Column(db.Integer, primary_key=True)
    user_1 = db.Column(db.Integer)
    user_2 = db.Column(db.Integer)
    restaurant_name = db.Column(db.String(128))
    restaurant_address = db.Column(db.String(128))
    restaurant_picture = db.Column(db.String(256))
    meal_time = db.Column(db.String(64))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_1': self.user_1,
            'user_2': self.user_2,
            'restaurant_name': self.restaurant_name,
            'restaurant_address': self.restaurant_address,
            'restaurant_picture': self.restaurant_picture,
            'meal_time': self.meal_time
        }

    @staticmethod
    def validate(data):
        required_fields = ['accept_proposal', 'proposal_id']
        errors = []
        if type(data) != dict:
            errors.append({'error': 'item must be a dict'})
        else:
            for key in required_fields:
                if not key in data:
                    errors.append({key: "Required"})
                else:
                    if not data[key]:
                        errors.append({key: "Required"})
        return errors
