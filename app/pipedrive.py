import json
import os
import time
from flask import request, session, url_for, redirect, Blueprint, jsonify, current_app
from flask_oauthlib.client import OAuth, OAuthException
import requests
from app.models import UserPipedriveToken, Lead
from app.services.google_sheets import get_google_sheet_data
from app.services.pipedrive import manage_webhook, fetch_organization_data_with_token, fetch_creator_id_with_token
from app.utils import logger, create_response, match_company_name

pipedrive_bp = Blueprint("pipedrive", __name__)

oauth = OAuth()
pipedrive = oauth.remote_app(
    'pipedrive',
    consumer_key=os.getenv("PIPEDRIVE_CONSUMER_KEY"),
    consumer_secret=os.getenv("PIPEDRIVE_CONSUMER_SECRET"),
    request_token_params={'scope': 'leads'},
    base_url=os.getenv("PIPEDRIVE_BASE_URL_V1"),
    access_token_url=os.getenv("PIPEDRIVE_ACCESS_TOKEN_URL"),
    authorize_url=os.getenv("PIPEDRIVE_AUTHORIZE_URL"),
)


@pipedrive_bp.route('/')
def home():
    """Home route for Pipedrive Blueprint."""
    return jsonify({'message': 'Welcome to the Pipedrive Blueprint!'})


@pipedrive_bp.route('/auth/pipedrive')
def authenticate():
    """Handles Pipedrive OAuth authentication."""
    try:
        email = request.args.get('email')
        if email:
            user_token = UserPipedriveToken.get_token_by_email(email)
            if user_token and user_token.expiration_time > time.time():
                access_token = user_token.access_token
                existing_webhook = manage_webhook(
                    access_token,
                    os.getenv("PIPEDRIVE_SUBSCRIPTION_URL")
                )
                if existing_webhook:
                    return "Webhook already exists and is active."
                return redirect(url_for('pipedrive.home'))
        #   For testing, use ngrok link like this
        callback_url = os.getenv("PIPEDRIVE_CALLBACK_URL")
        # callback_url = url_for('pipedrive.authorized', _external=True, email=email)
        logger.info(f"Redirecting to Pipedrive with callback URL: {callback_url}")
        return pipedrive.authorize(callback=callback_url)

    except Exception as e:
        logger.error(f"Error during authentication: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@pipedrive_bp.route('/auth/pipedrive/authorized')
def authorized():
    """Handles the response from Pipedrive after authorization."""
    try:
        email = request.args.get('email')
        response = pipedrive.authorized_response()
        if response is None or 'access_token' not in response:
            error_message = (
                "Invalid response from Pipedrive. Check redirect URI, scopes, or authorization status."
            )
            logger.error(f"{error_message} Response: {response}")
            return jsonify({"error": error_message, "response": response}), 400

        access_token = response['access_token']
        session['pipedrive_token'] = (access_token, '')
        logger.info("Access Token saved in session.")

        if email:
            creator_id = fetch_creator_id_with_token(access_token)
            expiration_time = time.time() + 3600
            UserPipedriveToken.save_token(
                user_email=email,
                access_token=access_token,
                expiration_time=expiration_time,
                creator_id=creator_id
            )

        existing_webhook = manage_webhook(
            access_token,
            current_app.config.get("PIPEDRIVE_WEBHOOK_URL")
        )
        if existing_webhook:
            return "Webhook already exists and is active."

        return redirect(url_for('pipedrive.home'))

    except OAuthException as e:
        logger.error(f"OAuthException: {e}")
        logger.error(e.data)
        return jsonify({"error": "OAuthException occurred", "details": e.data}), 500
    except Exception as e:
        logger.error(f"Unexpected Exception: {e}", exc_info=True)
        return jsonify({"error": "Unexpected error occurred", "details": str(e)}), 500


@pipedrive_bp.route('/webhook/lead', methods=['POST'])
def process_new_lead_webhook():
    """Processes incoming webhook notifications for newly created leads."""
    try:
        data = request.json
        creator_id = data.get('data', {}).get('creator_id')
        if not creator_id:
            logger.warning("No creator_id found in the webhook data.")
            return jsonify({"error": "No creator_id found"}), 400

        user_token = UserPipedriveToken.get_token_by_creator_id(creator_id)

        if not user_token:
            logger.warning(f"No access token found for creator_id {creator_id}")
            return jsonify({"error": f"No access token for creator_id {creator_id}"}), 404

        access_token = user_token.access_token
        organization_id = data['data'].get('organization_id')
        organization_data = fetch_organization_data_with_token(organization_id, access_token)
        if 'error' in organization_data:
            # print(organization_data)
            error_details = organization_data.get('details', {})
            logger.error(f"Failed to fetch organization data")
            logger.error(error_details)
            return create_response(
                message="Failed to fetch organization data",
                data=error_details,
                status_code=401,
            )
        company_name = organization_data['data']['name']

        # return organization_data
        sheet_data, error = get_google_sheet_data()
        # sheet_data = get_google_sheet_data()
        if error:
            logger.error(f"Failed to fetch data from Google Sheets: {error}")
            return create_response(message="Failed to fetch data from Google Sheets", data={"details": error},
                                   status_code=500)

        # Compare with Google Sheets and save lead if matched
        for row in sheet_data:
            company_name_in_sheet = row[3].lower() if row[3] else ""
            if match_company_name(name_in_hubspot=company_name, name_in_sheet=company_name_in_sheet):
                # if company_name == company_name_in_sheet:
                if Lead.query.filter_by(company_name=company_name).first():
                    logger.info(f"Skipping: Company '{company_name}' already exists in the database.")
                    return create_response(message=f"Skipping: Company '{company_name}' already exists in the database."
                                           ,status_code=200)
                else:
                    Lead.create_and_save(
                        adviser_name=row[0],
                        lead_name=row[1],
                        linkedin_url=row[2],
                        lead_title=row[4],
                        company_name=row[3],
                        # domain=domain
                    )
                    logger.info(f"Lead for '{row[3]}' has been saved to the database.")
                    return create_response(message=f"Lead for '{company_name}' has been saved to the database.",
                                           status_code=200)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
