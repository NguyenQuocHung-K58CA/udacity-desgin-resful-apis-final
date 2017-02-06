from marshmallow import fields, Schema


class MealdateSchema(Schema):
    user_1 = fields.Integer()
    user_2 = fields.Integer()
    restaurant_name = fields.String()
    restaurant_address = fields.String()
    restaurant_picture = fields.String()
    meal_time = fields.String()

    proposal_id = fields.Integer(required=True)
    accept_proposal = fields.Boolean(required=True)