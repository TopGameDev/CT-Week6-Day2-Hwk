import os
import base64
from app import db, login
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False) 
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contact = db.relationship('Contact', backref='author', cascade='delete')
    token = db.Column(db.String(100), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    #Hash Password taken from User
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password'))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)
    
    # Create and Apply Token
    def get_token(self, expires_in=3600):
        # Set the start of the timer
        now = datetime.utcnow()
        # Check for how long token has been active
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # Create Token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        # Set Token Expiration
        self.token_expiration = now + timedelta(seconds=expires_in)
        # Save Token to database and Execute
        db.session.commit()
        return self.token
    
    # The ability to revoke an active token
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()

    # Create dictionary output for JSON file
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username
        }

@login.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False, unique=True)
    address = db.Column(db.String(50), nullable=False, unique=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<User {self.id}|{self.first_name}>"
    
    # Create dictionary output for JSON file, also added dictionary inside of dictionary for the related user of the contact
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'date_time': self.date_time,
            'user_id': self.user_id,
            'author': self.author.to_dict()
        }
    
