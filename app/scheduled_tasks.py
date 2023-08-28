from app import app
from app.routes import process_due_alerts

with app.app_context():
    process_due_alerts()
