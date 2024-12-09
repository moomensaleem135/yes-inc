from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flasgger import Swagger
from flask_migrate import Migrate
from app.config import Config
from app.models import User
from app.database import db
from app.auth import auth_bp
from app.webhook import webhook_bp

# Initialize Flask extensions
login_manager = LoginManager()
migrate = Migrate()
swagger = Swagger()


def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    :param config_class: Configuration class for the app. Default is Config.
    :return: Configured Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    swagger.init_app(app)

    # Set LoginManager settings
    login_manager.login_view = 'auth_blueprint.login'
    login_manager.login_message = "Please log in to access this page."

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp)

    # Define routes
    @app.route('/')
    def home():
        """
        Home route displaying links to API documentation and HubSpot access token authorization.
        """
        return """
              <h1>HubSpot Integration with Google Sheets to Match Leads</h1>
              <p>
                  To authenticate hubspot with the system, visit: 
                  <a href="http://localhost:5000/hubspot/auth" target="_blank">http://localhost:5000/hubspot/auth</a>
              </p>
              <p>
                  For the API documentation, visit: 
                  <a href="http://localhost:5000/apidocs/" target="_blank">http://localhost:5000/apidocs/</a>
              </p>
              """

    return app


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by ID for Flask-Login.

    :param user_id: The user ID stored in the session.
    :return: User instance or None if not found.
    """
    return User.query.get(int(user_id))
