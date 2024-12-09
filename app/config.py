from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()


class Config:
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    CODE = os.getenv('CODE')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SPREADSHEET_SHEET_NAME = os.getenv('SPREADSHEET_SHEET_NAME')
    SCOPE = os.getenv('SCOPE')
    USER_ID = os.getenv('USER_ID')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY')
