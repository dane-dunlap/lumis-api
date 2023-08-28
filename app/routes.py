import requests
import atexit
from bs4 import BeautifulSoup
import openai
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from dotenv import load_dotenv
from . import app, db
from .models import Alert,User
from datetime import datetime, timedelta, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from werkzeug.security import generate_password_hash



logging.basicConfig(level=logging.INFO)






load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
sendgrid_key = os.environ.get('SENDGRID_KEY')
news_api_key = os.environ.get('NEWS_API_KEY')
news_api_endpoint = "https://newsapi.org/v2/everything"



@app.route('/api/create_alert', methods=['POST'])
def set_alert():
    data = request.json
    company_name = '"' + data['company'].strip() + '"'
    cadence = data['cadence'].strip()
    user_email = data['email'].strip()

    if not company_name or not cadence or not user_email:
        return jsonify({"message": "Fields cannot be empty"}), 400

    if cadence == "Daily":
        next_due_date = datetime.utcnow().date() + timedelta(days=1)
    else:
        next_due_date = datetime.utcnow().date() + timedelta(days=7)

    new_alert = Alert(company_name=company_name, cadence=cadence, user_email=user_email,next_due_date=next_due_date)
    
    try:
        db.session.add(new_alert)
        db.session.commit()
        send_lumis(new_alert)
        return jsonify({"message": "Success"}), 201
    except:
        return jsonify({"message": "Error saving to database"}), 500

    


def get_days_from_cadence(cadence):
    if cadence == "daily":
        return 1
    elif cadence == "weekly":
        return 7
    else:
        # Default to daily if the cadence is not recognized
        return 1





def articles_summarizer(articles):
    article_contents = [article['content'] for article in articles]
    summaries = []
    for content in article_contents:
        prompt = f"Provide a concise summary for the following news article:\n\n{content}"
        response = openai.Completion.create(
        model="text-davinci-003",  # or another suitable model
        prompt=prompt,
        max_tokens=150  # Adjust based on the length you want
        )
        summaries.append(response.choices[0].text.strip())
    
    combined_content = "\n\n".join(summaries)
    prompt = f"Provide a high-level summary of the following news article summaries:\n\n{combined_content}"

    response = openai.Completion.create(
        model="text-davinci-003",  # or another suitable model
        prompt=prompt,
        max_tokens=100  # Adjust based on the length you want
    )
    final_overall_summary = response.choices[0].text.strip()
    return final_overall_summary


def send_lumis(alert):
    articles = fetch_articles_for_alert(alert)
    #final_summary = articles_summarizer(articles)
    final_summary = "Apple has released two new features for iOS users – Remove Subject From Background and Create and Save Your Own Stickers – to enhance their photo-editing experience. Remove Subject offers the ability to quickly and easily erase unwanted people and objects from photos, while Create and Save Your Own Stickers lets users turn their own snapshots and text into custom stickers. Additionally, the AirPods Pro 2 has been upgraded to include improved sound quality, active noise cancellation, spatial audio, transparency mode, and"
    
    recipient_email = alert.user_email
    url_list = [article['url'] for article in articles]
    cadence = alert.cadence
    company_name = alert.company_name
    subject = f"Lumis Alert: {company_name}"
    send_email(subject,final_summary,recipient_email,url_list,cadence,company_name)
    
    return jsonify({"message": "Success."}), 200


def fetch_articles_for_alert(alert):
    params = {
        'q': '"' + alert.company_name + '"',
        'from': date.today(),
        'to': date.today() - timedelta(days=get_days_from_cadence(alert.cadence)),
        'apiKey': news_api_key,
        'pageSize': 2, 
        'language': 'en'
    }

    response = requests.get(news_api_endpoint, params=params)

    if response.status_code == 200:
        articles = response.json()['articles']
        if articles:
            return articles
        else:
            return jsonify({"message": "No articles found for this alert."}), 404
    else:
        print(f"Error {response.status_code}: {response.text}")
        return jsonify({"message": f"Error fetching articles. API responded with {response.status_code}"}), 500


def send_email(subject, summary,recipient_email,urls,cadence,company_name):
    
    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
    from_email = Email("danecooperdunlap@gmail.com")
    to_email = To(recipient_email)
    html_content = render_template('email.html', article_summary=summary,urls = urls,cadence=cadence,company_name=company_name)
    content = Content("text/html", html_content)
    mail = Mail(from_email, to_email, subject, content)
    
    
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response.status_code

def process_due_alerts():
    logging.info("Started processing due alerts")
    with app.app_context():
        due_alerts = Alert.query.filter_by(next_due_date=date.today()).all()
        for alert in due_alerts:
            send_lumis(alert)
    logging.info("Finished processing due alerts")


    
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    form = RegistrationForm(data=data, csrf_enabled=False)  # We're not using CSRF here.

    if form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "Registration successful"})

    return jsonify({"message": "Validation failed", "errors": form.errors}), 400