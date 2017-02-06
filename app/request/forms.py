from marshmallow import Schema, fields


class RequestSchema(Schema):
    meal_type = fields.String(required=True)
    location_string = fields.String(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    meal_time = fields.DateTime(required=True)
    filled = fields.Boolean()
    user_id = fields.Integer()