import requests
from flask import current_app
import time
from app.models import AccessToken


def make_hubspot_api_request(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 401:
            print("Unauthorized token, refreshing token...")
            AccessToken.delete_all_tokens()
            refresh_hubspot_token()
            time.sleep(20)
            new_token = AccessToken.get_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return None, response.text

        return response.json(), None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None, f"Request failed: {str(e)}"


def refresh_hubspot_token():
    try:
        auth_url = "http://localhost:5000/hubspot/auth"
        response = requests.get(auth_url, allow_redirects=True)
        if response.history:
            print(f"Redirected {len(response.history)} times")
            final_redirect_url = response.url
            print("Final destination:", final_redirect_url)
            final_response = requests.get(final_redirect_url)
            if final_response.status_code == 200:
                print("Successfully refreshed HubSpot token after final redirect.", final_response.json())
            else:
                print(f"Failed to refresh HubSpot token at final URL: {final_response.status_code}")
        else:
            print("No redirects occurred.")
            if response.status_code == 200:
                print("Successfully refreshed HubSpot token.")
            else:
                print(f"Failed to refresh HubSpot token: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing HubSpot token: {e}")


def get_hubspot_company_details(contact_id):
    try:
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/companies"
        token = AccessToken.get_token()
        if token:
            headers = {"Authorization": f"Bearer {token.access_token}"}
        else:
            headers = {"Authorization": "Bearer "}
        response_data, error = make_hubspot_api_request(url, headers)

        if error:
            return None, error

        if response_data.get("results"):
            company_id = response_data["results"][0].get("id")
            if company_id:
                url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
                response_data, error = make_hubspot_api_request(url, headers)
                if error:
                    return None, error
                return response_data, None
        return None, "No company associated"
    except Exception as e:
        print(f"Error in get_hubspot_company_details: {e}")
        return None, f"Error: {str(e)}"


def get_google_sheet_data():
    try:
        google_sheets_api_key = current_app.config['GOOGLE_SHEETS_API_KEY']
        spreadsheet_id = current_app.config['SPREADSHEET_ID']
        spreadsheet_sheet_name = current_app.config['SPREADSHEET_SHEET_NAME']
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{spreadsheet_sheet_name}?key={google_sheets_api_key}"

        response_data, error = make_hubspot_api_request(url)
        if error:
            return None, error

        return response_data.get("values", []), None
    except Exception as e:
        print(f"Error in get_google_sheet_data: {e}")
        return None, f"Error: {str(e)}"
