from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from app.routes import main, stock_routes
    app.register_blueprint(main)
    app.register_blueprint(stock_routes)
    
    return app 