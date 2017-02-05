from flask import Blueprint


mealdate = Blueprint('mealdate', __name__)


from . import views