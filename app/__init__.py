from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flasgger import Swagger
from flask_migrate import Migrate
from app.config import Config
from app.models import User
from app.database import db
from app.auth import auth_bp
from app.webhook import webhook_bp

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    migrate = Migrate(app, db)
    app.config.from_object(Config)  # This will load the SQLALCHEMY_DATABASE_URI from Config
    db.init_app(app)
    login_manager.init_app(app)
    Swagger(app)
    app.register_blueprint(auth_bp, url_prefix='/auth', name='auth_blueprint')
    app.register_blueprint(webhook_bp, name='webhook_blueprint')

    @app.route('/')
    def home():
        return redirect(url_for('flasgger.apidocs'))
    return app
