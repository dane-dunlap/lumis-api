from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    followed_apps = db.relationship('App', secondary='user_app', backref='followers')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(200), unique=True, nullable=False)
    current_version = db.Column(db.String(50), nullable=False)
    release_notes = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)


class UserApp(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), primary_key=True)
    date_followed = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    cadence = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    last_email_sent = db.Column(db.DateTime)
    article_URLs = db.Column(db.Text)  # This can be a serialized list or JSON.
    next_due_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'cadence': self.cadence,
            'user_email': self.user_email,
            'next_due_date': self.next_due_date.strftime('%Y-%m-%d')  # assuming it's a date object
        }

