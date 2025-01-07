from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', 'your_default_hubspot_api_key')
    CLIENT_ID = os.getenv('CLIENT_ID', 'your_default_client_id')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'your_default_client_secret')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/hubspot/callback')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY', 'your_default_google_sheets_api_key')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', 'your_default_spreadsheet_id')
    SPREADSHEET_SHEET_NAME = os.getenv('SPREADSHEET_SHEET_NAME', 'Sheet1')
    SCOPE = os.getenv('SCOPE', 'oauth crm.objects.contacts.read')
    USER_ID = os.getenv('USER_ID')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'your-database-path')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False')
    HUBSPOT_BASE_URL = os.getenv('HUBSPOT_BASE_URL', 'https://app.hubspot.com/oauth')
    HUBSPOT_TOKEN_URL = os.getenv('HUBSPOT_TOKEN_URL', 'https://api.hubapi.com/oauth/v1/token')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    BASE_URL = os.getenv('BASE_URL', 'localhost')
    PIPEDRIVE_CONSUMER_KEY = os.getenv('PIPEDRIVE_CONSUMER_KEY', '')
    PIPEDRIVE_CONSUMER_SECRET = os.getenv('PIPEDRIVE_CONSUMER_SECRET', '')
    PIPEDRIVE_BASE_URL_V1 = os.getenv('PIPEDRIVE_BASE_URL_V1', 'https://api.pipedrive.com/v1/')
    PIPEDRIVE_BASE_URL_V2 = os.getenv('PIPEDRIVE_BASE_URL_V2', 'https://api.pipedrive.com/v2/')
    PIPEDRIVE_ACCESS_TOKEN_URL = os.getenv('PIPEDRIVE_ACCESS_TOKEN_URL', 'https://oauth.pipedrive.com/oauth/token')
    PIPEDRIVE_AUTHORIZE_URL = os.getenv('PIPEDRIVE_AUTHORIZE_URL', 'https://oauth.pipedrive.com/oauth/authorize')
