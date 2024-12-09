from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(password=self.password, pwhash='')


class HubspotToken(db.Model):
    __tablename__ = 'hubspot_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return f'<Hubspot Token {self.id}>'


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    adviser_name = db.Column(db.String(255))
    lead_name = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    lead_title = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    domain = db.Column(db.String(255))

    def __repr__(self):
        return f'<Lead {self.lead_title}>'

    @classmethod
    def create_and_save(cls, adviser_name, lead_name, linkedin_url, lead_title, company_name, domain):
        try:
            new_lead = cls(
                adviser_name=adviser_name,
                lead_name=lead_name,
                linkedin_url=linkedin_url,
                lead_title=lead_title,
                company_name=company_name,
                domain=domain
            )
            db.session.add(new_lead)
            db.session.commit()
            return new_lead, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)


class AccessToken(db.Model):
    __tablename__ = 'access_tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(255), nullable=False)
    expiration_time = db.Column(db.Float, nullable=False)

    def __init__(self, access_token, expiration_time):
        self.access_token = access_token
        self.expiration_time = expiration_time

    @staticmethod
    def get_token():
        return AccessToken.query.first()

    @staticmethod
    def save_token(access_token, expiration_time):
        token = AccessToken.query.first()
        if token:
            token.access_token = access_token
            token.expiration_time = expiration_time
        else:
            token = AccessToken(access_token, expiration_time)
            db.session.add(token)
        db.session.commit()

    @staticmethod
    def delete_token():
        token = AccessToken.query.first()
        if token:
            db.session.delete(token)
            db.session.commit()

    @staticmethod
    def delete_all_tokens():
        token = AccessToken.query.all()
        if token:
            db.session.delete(token)
            db.session.commit()
