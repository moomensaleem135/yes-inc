import requests
from flask import current_app, jsonify
import time
import urllib.parse
from app.models import AccessToken
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def make_hubspot_api_request(url: str, headers: Optional[Dict[str, str]] = None,
                             params: Optional[Dict[str, str]] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Make a GET request to the HubSpot API, automatically handling token refresh if unauthorized (401).
    :return: A tuple of the response JSON data or None and an error message or None.
    """
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 401:
            logger.warning("Unauthorized token, refreshing token...")
            AccessToken.delete_all_tokens()
            refresh_hubspot_token()
            time.sleep(10)
            new_token = AccessToken.get_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token.access_token}"
                response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f"Failed request with status code: {response.status_code}")
            return None, response.text
        logger.info(f"Request successful for URL: {url}")
        return response.json(), None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None, f"Request failed: {str(e)}"


def refresh_hubspot_token() -> None:
    """
    Refreshes the HubSpot OAuth token by triggering the authorization flow.
    """
    try:
        auth_url = "http://localhost:5000/hubspot/auth"
        response = requests.get(auth_url, allow_redirects=True)
        if response.history:
            logger.info(f"Redirected {len(response.history)} times")
            final_redirect_url = response.url
            logger.info(f"Final destination: {final_redirect_url}")
            final_response = requests.get(final_redirect_url)
            if final_response.status_code == 200:
                logger.info("Successfully refreshed HubSpot token after final redirect.")
            else:
                logger.error(f"Failed to refresh HubSpot token at final URL: {final_response.status_code}")
        else:
            logger.info("No redirects occurred.")
            if response.status_code == 200:
                logger.info("Successfully refreshed HubSpot token.")
            else:
                logger.error(f"Failed to refresh HubSpot token: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing HubSpot token: {e}")
        logger.error("Invalid or expired token. To get a fresh access token,"
                     " click on this link: http://localhost:5000/hubspot/auth")


def get_hubspot_company_details(contact_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Retrieves the company details associated with a HubSpot contact.
    :return: A tuple containing the company details or None and an error message or None.
    """
    try:
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/companies"
        token = AccessToken.get_token()
        headers = {"Authorization": f"Bearer {token.access_token}"} if token else {"Authorization": "Bearer "}
        response_data, error = make_hubspot_api_request(url, headers)
        if error:
            logger.error(f"Error retrieving company details: {error}")
            return None, error
        if response_data.get("results"):
            company_id = response_data["results"][0].get("id")
            if company_id:
                url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
                response_data, error = make_hubspot_api_request(url, headers)
                if error:
                    logger.error(f"Error retrieving company info: {error}")
                    return None, error
                logger.info(f"Successfully retrieved company details for contact {contact_id}.")
                return response_data, None
        logger.warning(f"No company associated with contact {contact_id}")
        return None, "No company associated"
    except Exception as e:
        logger.error(f"Error in get_hubspot_company_details: {e}")
        return None, f"Error: {str(e)}"


def get_google_sheet_data() -> Tuple[Optional[list], Optional[str]]:
    """
    Retrieves data from a specified Google Sheet.
    :return: A tuple containing the sheet data as a list or None and an error message or None.
    """
    try:
        google_sheets_api_key = current_app.config['GOOGLE_SHEETS_API_KEY']
        spreadsheet_id = current_app.config['SPREADSHEET_ID']
        spreadsheet_sheet_name = current_app.config['SPREADSHEET_SHEET_NAME']
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{spreadsheet_sheet_name}?key={google_sheets_api_key}"
        response_data, error = make_hubspot_api_request(url)
        if error:
            logger.error(f"Error retrieving Google Sheet data: {error}")
            return None, error

        logger.info("Successfully retrieved data from Google Sheet.")
        return response_data.get("values", []), None
    except Exception as e:
        logger.error(f"Error in get_google_sheet_data: {e}")
        return None, f"Error: {str(e)}"


def get_hubspot_oauth_url(user_id: str, client_id: str, redirect_uri: str, scope: str) -> str:
    """
    Generates the HubSpot OAuth authorization URL.
    :return: Fully formatted HubSpot OAuth URL.
    """
    base_url = current_app.config['HUBSPOT_BASE_URL']
    hubspot_url = f"{base_url}/{user_id}/authorize"
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
    }
    return f"{hubspot_url}?{urllib.parse.urlencode(params)}"


def exchange_authorization_code_and_save(code: str) -> Dict[str, str]:
    """
    Exchanges an authorization code for an access token and saves it to the database.
    :return: A dictionary with the access token details or an error message.
    """
    token_url = current_app.config['HUBSPOT_TOKEN_URL']
    data = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET'],
        'redirect_uri': current_app.config['REDIRECT_URI'],
        'code': code
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get('access_token')
        expires_in = response_data.get('expires_in', 3600)
        expiration_time = (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
        AccessToken.save_token(access_token, expiration_time)
        logger.info(f"Access token saved successfully. Expiration time: {expiration_time}")
        return {
            "access_token": access_token,
            "expires_in": expires_in,
            "expiration_time": expiration_time
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging authorization code: {e}")
        return {"error": f"HTTP request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def create_response(message: Optional[str] = None, data: Optional[Dict] = None, error: Optional[Any] = None,
                    status_code: int = 200) -> Tuple:
    """
    Helper function to create consistent API responses.
    :return: Flask response object.
    """
    response = {
        "message": message,
        "data": data,
        "error": error,
    }
    # Remove keys with None values for cleaner responses
    response = {key: value for key, value in response.items() if value is not None}
    return jsonify(response), status_code
