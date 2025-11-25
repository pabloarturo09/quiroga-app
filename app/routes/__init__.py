from flask import Blueprint, send_from_directory

main_bp = Blueprint('main', __name__)

@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory('..', 'manifest.json')

@main_bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

from app.routes import auth_routes
from app.routes import admin_routes
from app.routes import inventory_management_routes
from app.routes import reservations_management_routes
from app.routes import users_management_routes
from app.routes import user_routes
