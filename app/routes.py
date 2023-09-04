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
news_api_endpoint = "http://eventregistry.org/api/v1/article/getArticles"



@app.route('/api/create_alert', methods=['POST'])
def set_alert():
    data = request.json
    company_name = data['company'].strip()
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
        return jsonify({"message": "Success","alert": new_alert.to_dict()}), 201
    except:
        return jsonify({"message": "There was an error saving this alert"}), 500






def get_days_from_cadence(cadence):
    if cadence == "daily":
        return 1
    elif cadence == "weekly":
        return 7
    else:
        # Default to daily if the cadence is not recognized
        return 1


def articles_summarizer(news_api_response):
    articles = news_api_response['articles']
    company_name = news_api_response['company_name']
    cadence = news_api_response['cadence']
    if cadence == "Daily":
        cadence = "day"
    else:
        cadence = "week"
    
    article_contents = [article['body'] for article in articles]
    summaries = []
    for content in article_contents:
        messages = [
            {"role": "user", "content": f"Provide a concise summary for the following news article:\n\n{content}"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens= 1000
        )
        summaries.append(response.choices[0].message['content'].strip())
        print(response.choices[0].message['content'].strip())
        print("xxxxxxxxxxxxxxxxxxxx")
    
    combined_content = "\nArticle Summary:\n" + "\nArticle Summary:\n".join(summaries)
    messages = [
        {
            "role": "user",
            "content": f"Each of these is a summary of the top news for {company_name} over the last {cadence} , please provide a high-level summary for {company_name} over the last {cadence}. Please only include information about {company_name}:\n\n{combined_content}"
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000
    )
    
    final_overall_summary = response.choices[0].message['content'].strip()
    print(response)
    print("overall summary")
    print("===============================")
    print(final_overall_summary)
    return final_overall_summary


@app.route('/api/send_alert', methods=['POST'])
def send_lumis():
    alert_data = request.json.get('alert')
    alert_id = alert_data['id']
    alert = db.session.query(Alert).filter_by(id=alert_id).first()
    subject = f"Lumis Alert: {alert.company_name}"
    recipient_email = alert.user_email
    news_api_response = fetch_articles_for_alert(alert)
    if "error" in news_api_response:
        final_summary = news_api_response["message"]
        url_list = []
        send_email(subject,final_summary,recipient_email,url_list,alert)
    else:
        final_summary = articles_summarizer(news_api_response)    
        url_list = [article['url'] for article in news_api_response["articles"]]    
        send_email(subject,final_summary,recipient_email,url_list,alert)
    
    try:
        return jsonify({"message": "Success"}), 201
    except:
        return jsonify({"message": "There was an error sending this alert to email"}), 500


def fetch_articles_for_alert(alert):
    params = {
    "action": "getArticles",
    "keyword": '"'+ alert.company_name + '"',
    "articlesPage": 1,
    #"conceptURI":"https://en.wikipedia.org/wiki/Nvidia",
    "eventFilter": "skipArticlesWithoutEvent",
    "keywordLoc": "title",
    "articlesCount": 5,
    "lang": "eng",
    "dateStart": date.today() - timedelta(days=get_days_from_cadence(alert.cadence)), 
    "dateEnd": date.today(),
    "articlesSortBy": "sourceImportanceRank",
    "articlesArticleBodyLen": -1,
    "resultType": "articles",
    "includeArticleCategories":"True",
    "includeArticleConcepts": "True",
    "dataType": [
        "news",
        "pr"
    ],
    "apiKey": news_api_key,
    "forceMaxDataTimeWindow": 31
    }

    response = requests.get(news_api_endpoint, params=params)

    if response.status_code == 200:
        articles = response.json()['articles']['results']
        if articles:
            return {
                "articles": articles,
                "company_name": alert.company_name,
                "cadence": alert.cadence
            }
        else:
            return {"message": f"No recent news was found for {alert.company_name} over the alert period", "error": 404}

    else:
        print(f"Error {response.status_code}: {response.text}")
        return {"message": f"Error fetching articles. API responded with {response.status_code}", "error": 500}



def send_email(subject, summary,recipient_email,urls,alert):
    
    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
    from_email = Email("danecooperdunlap@gmail.com")
    to_email = To(recipient_email)
    cadence = alert.cadence
    company_name = alert.company_name
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
