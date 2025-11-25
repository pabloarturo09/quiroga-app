from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    from app.middleware import init_app
    init_app(app)
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
