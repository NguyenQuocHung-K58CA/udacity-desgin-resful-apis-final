from flask import request, jsonify
from flask import g
from flask import abort
from sqlalchemy import or_, and_


from app import db, auth
from app.models import Proposal, Request
from . import proposal


@proposal.route('/api/v1/proposals', methods=['GET'])
@auth.login_required
def get_all_proposals():
    user = g.user
    proposals = Proposal.query.filter_by(user_proposed_to=user.id).all()
    proposals = [proposal.serialize for proposal in proposals]
    return jsonify({'proposals': proposals}), 200


@proposal.route('/api/v1/proposals', methods=['POST'])
@auth.login_required
def create_new_proposal():
    errors = Proposal.validate(request.json)

    if len(errors) == 0:
        user_proposed_from = g.user.id
        request_id = request.json.get('request_id')

        req = Request.query.filter(and_(Request.id == request_id, Request.user_id != user_proposed_from)).first()
        if req is None:
            return jsonify({'errors': 'Request is not exist'})
        else:
            user_proposed_to = req.user_id
            proposal = Proposal(request_id=request_id,
                                user_proposed_from=user_proposed_from, user_proposed_to=user_proposed_to)
            db.session.add(proposal)
            db.session.commit()
            return jsonify({'response': True}), 201
    else:
        return jsonify({'errors': errors})


@proposal.route('/api/v1/proposals/<int:id>', methods=['GET'])
@auth.login_required
def get_proposal_by_id(id):
    user = g.user
    proposals = Proposal.query.filter(or_(
        Proposal.user_proposed_from == user.id,
        Proposal.user_proposed_to == user.id
        )).all()
    proposals = [proposal.serialize for proposal in proposals]
    return jsonify({'proposals': proposals})


@proposal.route('/api/v1/proposals/<int:id>', methods=['PUT'])
@auth.login_required
def update_proposal(id):
    errors = Proposal.validate(request.json)
    if len(errors) > 0:
        return jsonify({'errors': errors}), 400

    user = g.user
    proposal = Proposal.query.filter(and_(
        Proposal.id == id,
        Proposal.user_proposed_from == user.id
        ))

    if not proposal:
        abort(400)

    user_proposed_from = user.id
    request_id = request.json.get('request_id')

    req = Request.query.filter(and_(Request.id == request_id, Request.user_id != user_proposed_from)).first()
    if req is None:
        return jsonify({'errors': 'Request is not exist'})
    else:
        user_proposed_to = req.user_id
        proposal = {
            'request_id': request_id,
            'user_proposed_from': user_proposed_from,
            'user_proposed_to': user_proposed_to
        }
        proposal.update(proposal)
        db.session.commit()
        return jsonify({'response': True}), 201


@proposal.route('/api/v1/proposals/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_proposal(id):
    user = g.user
    proposal = Proposal.query.filter(and_(
        Proposal.id == id,
        user.id == Proposal.user_proposed_from
    )).first()

    if proposal is None:
        abort(400)

    db.session.delete(proposal)
    db.session.commit()
    return jsonify({'response': True}), 200