from marshmallow import Schema, fields


class ProposalSchema(Schema):
    user_proposed_to = fields.Integer()
    user_proposed_from = fields.Integer()
    request_id = fields.Integer(required=True)
    filled = fields.Boolean()