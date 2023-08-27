from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lumis.db'
CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
