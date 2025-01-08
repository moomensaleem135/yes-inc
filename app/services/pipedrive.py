import os
import requests
from app.utils import logger

PIPEDRIVE_BASE_URL_V1 = os.getenv("PIPEDRIVE_BASE_URL_V1"),


def manage_webhook(access_token: str, subscription_url: str) -> dict or None:
    """Manages Pipedrive webhooks."""
    url = "https://api.pipedrive.com/v1/webhooks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Check for existing webhooks
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch existing webhooks: {response.json()}")
        return None

    webhooks = response.json().get('data', [])
    for webhook in webhooks:
        if (
                webhook.get('event_action') == 'create' and
                webhook.get('event_object') == 'lead' and
                webhook.get('subscription_url') == subscription_url and
                webhook.get('is_active')
        ):
            logger.info("A similar webhook already exists.")
            return webhook

    payload = {
        "version": "2.0",
        "type": "general",
        "event_action": "create",
        "event_object": "lead",
        "subscription_url": subscription_url
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        logger.info("Webhook created successfully.")
        return None
    else:
        logger.error(f"Failed to create webhook: {response.json()}")
        return None


def fetch_organization_data_with_token(organization_id: str, access_token: str) -> dict:
    """
    Fetches organization data from Pipedrive API using an access token.

    Args:
        organization_id (int): The ID of the organization to fetch.
        access_token (str): The OAuth access token.

    Returns:
        dict: The organization data if successful, or an error message.
    """
    if not access_token:
        return {"error": "Access token is missing."}
    # url = f"{PIPEDRIVE_BASE_URL_V1}/organizations/{organization_id}"
    url = f"https://api.pipedrive.com/v1/organizations/{organization_id}"

    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  # Return organization data
        else:
            return {
                "error": f"Failed to fetch organization. Status code: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        logger.error(f"An exception occurred while fetching organization data.: {str(e)}")
        return {"error": "An exception occurred while fetching organization data.", "details": str(e)}


def fetch_creator_id_with_token(access_token):
    try:
        url = 'https://api.pipedrive.com/v1/users/me'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return user_data['data']['id']  # Extract the creator_id from the response
        else:
            raise Exception(f"Failed to fetch user details: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"An exception occurred while fetching user data.: {str(e)}")
