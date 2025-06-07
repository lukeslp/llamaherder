from flask import Blueprint

# Create the social blueprint
social_bp = Blueprint('social', __name__)

# Import all routes
from api.routes.social import reddit

# Return the blueprint for registration
def get_blueprint():
    return social_bp 