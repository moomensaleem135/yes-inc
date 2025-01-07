from typing import Tuple, Optional
import requests
from app.utils import logger
import os


def get_google_sheet_data() -> Tuple[Optional[list], Optional[str]]:
    """
    Retrieves data from a specified Google Sheet.
    :return: A tuple containing the sheet data as a list or None and an error message or None.
    """
    try:
        google_sheets_api_key = os.getenv('GOOGLE_SHEETS_API_KEY')
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        spreadsheet_sheet_name = os.getenv('SPREADSHEET_SHEET_NAME')
        if not google_sheets_api_key or not spreadsheet_id or not spreadsheet_sheet_name:
            error_message = "Missing required environment variables."
            logger.error(error_message)
            return None, error_message
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{spreadsheet_sheet_name}?key={google_sheets_api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            error_message = f"Failed to retrieve data. Status code: {response.status_code}, Message: {response.text}"
            logger.error(error_message)
            return None, error_message
        response_data = response.json()
        logger.info("Successfully retrieved data from Google Sheet.")
        return response_data.get("values", []), None
    except Exception as e:
        logger.error(f"Error in get_google_sheet_data: {e}")
        return None, f"Error: {str(e)}"
