from typing import Dict, Any

from flask import Blueprint, request, jsonify
from flask_login import login_user
from app import db
from app.models import User, Lead
from flasgger import swag_from
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import BadRequest
from app.swagger_docs import sign_up_docs, log_in_docs, hubspot

auth_bp = Blueprint('auth', __name__)
HUBSPOT_API_KEY = '52f67ccd-5bbb-43b6-98d7-bcdf03f9cb99'


@auth_bp.route('/sign-up/', methods=['POST'])
@swag_from(sign_up_docs)
def sign_up():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Invalid JSON format")
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"message": "User already exists"}), 400
        new_user = User()
        new_user.email = email
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error", "details": str(e.orig)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@swag_from(log_in_docs)
def login() -> Any:
    try:

        data: Dict[str, str] = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400
        email: str = data.get('email', '').strip()
        password: str = data.get('password', '').strip()
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        user = User.query.filter_by(email=email).first()
        if user:  # and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 400

