from flask import Blueprint, request, redirect, current_app
from app.models import Lead
from flasgger import swag_from
from app.swagger_docs import hubspot
from app.utils import *

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Handles incoming webhook events, fetches company details from HubSpot,
    and compares them with data in Google Sheets to create leads.
    """
    try:
        data = request.get_json()
        if not data:
            logger.error("No data received in webhook request.")
            return create_response(message="No data received", status_code=400)

        contact_id = data[0].get('objectId')
        if not contact_id:
            logger.error("No objectId found in webhook data.")
            return create_response(message="No objectId found in webhook data", status_code=400)

        # Fetch company details from HubSpot
        company_details, error = get_hubspot_company_details(contact_id)
        if error:
            logger.error(f"Failed to fetch company details for contact {contact_id}: {error}")
            return create_response(message="Failed to fetch company details", data={"details": error}, status_code=500)

        company_name = company_details["properties"].get("name", "N/A").lower()
        domain = company_details["properties"].get("domain", "N/A")

        # Fetch data from Google Sheets
        sheet_data, error = get_google_sheet_data()
        if error:
            logger.error(f"Failed to fetch data from Google Sheets: {error}")
            return create_response(message="Failed to fetch data from Google Sheets", data={"details": error},
                                   status_code=500)

        # Compare with Google Sheets and save lead if matched
        for row in sheet_data:
            company_name_in_sheet = row[3].lower() if row[3] else ""
            if company_name == company_name_in_sheet:
                if Lead.query.filter_by(company_name=company_name).first():
                    logger.info(f"Skipping: Company '{company_name}' already exists in the database.")
                else:
                    Lead.create_and_save(
                        adviser_name=row[0],
                        lead_name=row[1],
                        linkedin_url=row[2],
                        lead_title=row[4],
                        company_name=company_name,
                        domain=domain
                    )
                    logger.info(f"Lead for '{company_name}' has been saved to the database.")
                    return create_response(message=f"Lead for '{company_name}' has been saved to the database.",
                                           status_code=200)

        logger.info("No matched company found in Google Sheets.")
        return create_response(message="No matched company found in Google Sheets.", status_code=200)

    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return create_response(message="An error occurred", data={"details": str(e)}, status_code=500)


@webhook_bp.route('/hubspot/auth', methods=['GET'])
@swag_from(hubspot)
def authorize_and_exchange():
    """
    Redirects the user to the HubSpot OAuth authorization URL.
    """
    try:
        client_id = current_app.config['CLIENT_ID']
        redirect_uri = current_app.config['REDIRECT_URI']
        scope = current_app.config['SCOPE']
        user_id = current_app.config['USER_ID']

        auth_url = get_hubspot_oauth_url(
            user_id=user_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope
        )
        logger.info("Redirecting user to HubSpot OAuth URL.")
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"Error in HubSpot authorization: {e}")
        return create_response(message="Failed to generate authorization URL", data={"details": str(e)},
                               status_code=500)


@webhook_bp.route('/hubspot/callback', methods=['GET'])
@swag_from(hubspot)
def callback():
    """
    Handle HubSpot OAuth callback and exchange authorization code for access token.
    """
    try:
        code = request.args.get('code')
        if not code:
            logger.error("No authorization code provided in callback.")
            return create_response(message="No authorization code provided.", status_code=400)

        # Exchange authorization code and save the token
        result = exchange_authorization_code_and_save(code)

        if "error" in result:
            logger.error(f"Error during token exchange: {result['error']}")
            return create_response(message="Error during token exchange", data={"details": result["error"]},
                                   status_code=500)

        logger.info(f"Authorization successful for user, access token generated.")
        return create_response(
            message="Authorization successful! Access token generated for user",
            data={"access_token": result["access_token"], "expires_in": result["expires_in"]},
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error in callback handling: {e}")
        return create_response(message="Error during OAuth callback", data={"details": str(e)}, status_code=500)
