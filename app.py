from flask import Flask
from controllers.location_controller import location_bp
from controllers.recommendation_controller import recommendation_bp
from controllers.auth_controller import auth_bp
from controllers.booking_controller import booking_bp
from config import Config
from db import init_db
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    # Load Configuration
    app.config.from_object(Config)

    # Initialize MongoDB
    with app.app_context():
        app.db = init_db() 

    # Initialize Swagger
    swagger = Swagger(app)

    # Register Blueprints
    app.register_blueprint(location_bp, url_prefix='/api')
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(booking_bp, url_prefix='/api')

    # Startup Tasks 
    # from services.scrape_service import ScrapeService
    # with app.app_context():
    #     scrape_service = ScrapeService()
    #     scrape_service.scrape()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
