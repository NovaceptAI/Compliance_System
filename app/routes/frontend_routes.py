from flask import Blueprint, render_template

frontend_blueprint = Blueprint('frontend', __name__)


@frontend_blueprint.route('/')
def landing():
    return render_template('landing.html')
