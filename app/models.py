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
