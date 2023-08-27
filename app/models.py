from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
     
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    cadence = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    last_email_sent = db.Column(db.DateTime)
    article_URLs = db.Column(db.Text)  # This can be a serialized list or JSON.
    next_due_date = db.Column(db.Date, nullable=True)



