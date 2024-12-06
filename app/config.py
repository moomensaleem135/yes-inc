import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:suleman01@localhost/yes-inc'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'supersecretkey'

    GOOGLE_SHEET_ID = 'https://docs.google.com/spreadsheets/d/1WNaIWXQK5tS-N2Mn3qeSkrDVEyIY7N105d7-VonXZ28/edit?usp=sharing'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SHEET_ID = os.getenv('SHEET_ID')
