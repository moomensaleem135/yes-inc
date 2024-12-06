from flask import Blueprint, request, jsonify, make_response, redirect
from app import db
from app.models import User, Lead
from flasgger import swag_from
from hubspot.crm.contacts import ApiException
from hubspot import HubSpot
from app.swagger_docs import hubspot
import requests
import urllib.parse

webhook_bp = Blueprint('auth', __name__)

client = HubSpot()


@webhook_bp.route('/webhook', methods=['POST'])
@swag_from(hubspot)
def webhook_handler():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        print(f"Webhook received: {data}")

        # Extract objectId (contact ID)
        contact_id = data[0].get('objectId')
        if not contact_id:
            return jsonify({"error": "No objectId found"}), 400

        # Fetch contact details using the HubSpot API
        print("object Id", contact_id)

        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/companies"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"}
        print(url, headers)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch contact details", "details": response.text}), 500
        association_details = response.json()
        print(association_details)
        if association_details.get("results"):
            company_id = association_details["results"][0].get("id")
            print(f"Association ID: {company_id}")
            if company_id:
                url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
                headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}"}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return jsonify({"error": "Failed to fetch contact details", "details": response.text}), 500
                company_details = response.json()
                company_name = company_details["properties"].get("name", "N/A")
                domain = company_details["properties"].get("domain", "N/A")
                print("company_name", company_name)
                api_key = GOOGLE_SHEETS_API_KEY
                spreadsheet_id = SPREADSHEET_ID
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{SPREADSHEET_SHEET_NAME}?key={api_key}"
                sheet_response = requests.get(url)
                if sheet_response.status_code != 200:
                    return jsonify(
                        {"error": "Failed to fetch data from Google Sheets", "details": sheet_response.text}), 500
                sheet_data = sheet_response.json()
                for row in sheet_data.get("values", []):
                    print("row", row)
                    company_name_in_sheet = row[3]
                    if company_name.lower() == company_name_in_sheet.lower():
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
                            db.session.rollback()  # Rollback in case of any error
                            print(e)
                            return jsonify({"error": f"Failed to save lead: {str(e)}"}), 500
                    print("No matched company")

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


@webhook_bp.route('/hubspot/auth', methods=['GET'])
@swag_from(hubspot)
def authorize_and_exchange():
    """Handle OAuth authorization and token exchange in one API."""

    # Step 1: Redirect user to HubSpot OAuth authorization URL
    hubspot_url = f"https://app.hubspot.com/oauth/{USER_ID}/authorize"
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
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
    user_id = request.args.get('user_id')  # Get the user_id passed earlier

    if not code:
        return jsonify({"error": "No authorization code provided."}), 400

    # Step 2: Exchange the authorization code for an access token
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code
    }

    try:
        # Make the POST request to exchange the code for an access token
        response = requests.post(token_url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            access_token = response_data.get('access_token')
            # Save the access token to use in subsequent API requests, associated with the user_id
            print(f"Access Token: {access_token}")

            # You can now associate the token with the user in your database
            # For example, save access_token to your database associated with user_id

            return jsonify({
                "message": f"Authorization successful! Access token generated for user {user_id}.",
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Error during token exchange", "details": response_data}), 500
    except Exception as e:
        return jsonify({"error": f"Error during token exchange: {str(e)}"}), 500
