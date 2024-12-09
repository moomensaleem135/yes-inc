from flask import Blueprint, request
from flask_login import login_user
from app.models import User, Lead
from flasgger import swag_from
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest
from app.swagger_docs import sign_up_docs, log_in_docs
from app.utils import create_response, logger

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/sign-up/', methods=['POST'])
@swag_from(sign_up_docs)
def sign_up():
    try:
        data = request.get_json()
        if not data:
            logger.error("Invalid JSON format received during sign-up request.")
            raise BadRequest("Invalid JSON format")

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            logger.warning("Sign-up attempt with missing email or password.")
            return create_response(
                error={"email": "Email is required", "password": "Password is required"},
                status_code=400
            )

        response, status_code = User.create_user(email=email, password=password)

        logger.info(f"User created successfully: {email}")
        return create_response(data=response, status_code=status_code)

    except BadRequest as e:
        logger.error(f"Bad request error: {e}")
        return create_response(error={"message": str(e)}, status_code=400)
    except Exception as e:
        logger.error(f"Error in sign-up: {e}")
        return create_response(error={"message": "Internal server error", "details": str(e)}, status_code=500)


@auth_bp.route('/login', methods=['POST'])
@swag_from(log_in_docs)
def login():
    try:
        data = request.get_json()
        if not data:
            logger.error("Invalid JSON format received during login attempt.")
            return create_response(error="Invalid JSON format", status_code=400)

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            logger.warning("Login attempt with missing email or password.")
            return create_response(
                error={"email": "Email is required", "password": "Password is required"},
                status_code=400
            )

        user = User.authenticate(email=email, password=password)

        if user:
            login_user(user)
            logger.info(f"Login successful for user: {email}")
            return create_response(message="Login successful", status_code=200)

        logger.warning(f"Failed login attempt for user: {email} (Invalid credentials)")
        return create_response(error="Invalid email or password", status_code=401)

    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {e}")
        return create_response(error={"message": "Database error", "details": str(e)}, status_code=500)
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return create_response(error={"message": "Something went wrong", "details": str(e)}, status_code=500)
