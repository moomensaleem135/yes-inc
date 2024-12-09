from flask import Blueprint, request, jsonify, redirect, current_app
from app import db
from app.models import User, Lead, AccessToken
from flasgger import swag_from
from hubspot import HubSpot
from app.swagger_docs import hubspot
import urllib.parse
from datetime import datetime, timedelta
from app.utils import *
webhook_bp = Blueprint('auth', __name__)

client = HubSpot()


@webhook_bp.route('/webhook', methods=['POST'])
@swag_from(hubspot)
def webhook_handler():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        contact_id = data[0].get('objectId')
        if not contact_id:
            return jsonify({"error": "No objectId found"}), 400
        company_details, error = get_hubspot_company_details(contact_id)
        if error:
            return jsonify({"error": "Failed to fetch company details", "details": error}), 500
        company_name = company_details["properties"].get("name", "N/A")
        domain = company_details["properties"].get("domain", "N/A")
        sheet_data, error = get_google_sheet_data()
        if error:
            return jsonify({"error": "Failed to fetch data from Google Sheets", "details": error}), 500
        for row in sheet_data:
            company_name_in_sheet = row[3]
            if company_name.lower() == company_name_in_sheet.lower():
                existing_lead = Lead.query.filter_by(company_name=company_name).first()
                if existing_lead:
                    print(f"Skipping: Company {company_name} already exists in the database.")
                else:
                    adviser_name = row[0]
                    lead_name = row[1]
                    linkedin_url = row[2]
                    lead_title = row[4]
                    new_lead = Lead(
                        adviser_name=adviser_name,
                        lead_name=lead_name,
                        linkedin_url=linkedin_url,
                        lead_title=lead_title,
                        company_name=company_name,
                        domain=domain
                    )
                    try:
                        db.session.add(new_lead)
                        db.session.commit()
                        return jsonify(
                            {"message": f"Lead for '{company_name}' has been saved to the database."}), 200
                    except Exception as e:
                        db.session.rollback()
                        print(e)
                        return jsonify({"error": f"Failed to save lead: {str(e)}"}), 500

        return jsonify({"message": "No matched company found in Google Sheets."}), 200

    except Exception as e:
        print("Error in webhook: ", e)
        return jsonify({"error": str(e)}), 400


@webhook_bp.route('/hubspot/auth', methods=['GET'])
@swag_from(hubspot)
def authorize_and_exchange():
    client_id = current_app.config['CLIENT_ID']
    redirect_uri = current_app.config['REDIRECT_URI']
    scope = current_app.config['SCOPE']
    user_id = current_app.config['USER_ID']

    # Step 1: Redirect user to HubSpot OAuth authorization URL
    hubspot_url = f"https://app.hubspot.com/oauth/{user_id}/authorize"
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
    }

    # Build the full OAuth URL and redirect the user
    auth_url = f"{hubspot_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@webhook_bp.route('/hubspot/callback', methods=['GET'])
@swag_from(hubspot)
def callback():
    """Handle HubSpot OAuth callback and exchange authorization code for access token."""
    code = request.args.get('code')
    user_id = request.args.get('user_id')

    if not code:
        return jsonify({"error": "No authorization code provided."}), 400

    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET'],
        'redirect_uri': current_app.config['REDIRECT_URI'],
        'code': code
    }

    try:
        response = requests.post(token_url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            access_token = response_data.get('access_token')
            expiration_time = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
            AccessToken.save_token(access_token, expiration_time)
            return jsonify({
                "message": f"Authorization successful! Access token generated for user {user_id}.",
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Error during token exchange", "details": response_data}), 500
    except Exception as e:
        return jsonify({"error": f"Error during token exchange: {str(e)}"}), 500
