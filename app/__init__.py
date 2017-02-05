from flask import Flask, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from app.utils.rate_limit import ratelimit, get_view_rate_limit


from config import app_config

db = SQLAlchemy()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    from models import User
    user_id = User.verify_auth_token(username_or_token)

    if not user_id is None:
        user = User.query.get_or_404(user_id)
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            print 'Invaild username or password'
            return False

    g.user = user
    return True


def create_app(config_name):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    @app.after_request
    def inject_x_rate_headers(response):
        limit = get_view_rate_limit()
        if limit and limit.send_x_headers:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))
        return response

    db.init_app(app)
    CORS(app)

    migrate = Migrate(app, db)

    from app import models

    from .oauth2 import oauth2 as oauth2_blueprint
    from .user import user as user_blueprint
    from .mealdate import mealdate as mealdate_blueprint
    from .proposal import proposal as proposal_blueprint
    from .request import request as request_blueprint

    app.register_blueprint(oauth2_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(mealdate_blueprint)
    app.register_blueprint(proposal_blueprint)
    app.register_blueprint(request_blueprint)

    # temporary route
    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    @app.route('/token')
    @ratelimit(limit=30, per=30 * 1)
    def index():
        return jsonify({'response': 'This is a rate limited response'})

    return app

# export FLASK_CONFIG=development
# export FLASK_APP=run.py

