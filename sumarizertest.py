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
from datetime import datetime, timedelta, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from werkzeug.security import generate_password_hash
from app.models import Alert,User


load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')


article_contents = ["Apple, Samsung, Nvidia and many others are ready to buy ARM shares during the IPO.The list also includes Intel, Cadence Design Systems, Synopsys and Alphabet\n\nBritish chipmaker ARM is preparing for an initial public offering (IPO), in which parent company SoftBank plans to raise money from interested customers.\n\nLast month, a report suggested that Apple and Samsung were planning to buy ARM shares once trading began. Now, a Reuters report says that Arm clients, including Apple and Samsung, will be among the investors in the IPO.\n\nIn addition to Apple and Samsung, ARM's IPO has attracted many high-profile investors from the tech and chip industry, including AMD, Nvidia, Intel, Cadence Design Systems, Synopsys, and Alphabet. These investors agreed to invest in the IPO at a valuation of between $50 billion and $55 billion, according to Reuters. SoftBank hopes to achieve this target valuation.",
                    "PM Narendra Modi meets CEO of Nvidia, discusses 'rich potential' India offers in world of AI - OrissaPOSTNew Delhi: Prime Minister Narendra Modi Monday met CEO of American software firm Nvidia Jensen Huang and they talked at length about the \"rich potential\" India offers in the world of Artificial Intelligence.\n\nIn a post on X, Modi said, \"Had an excellent meeting with Mr. Jensen Huang, the CEO of @nvidia. We talked at length about the rich potential India offers in the world of AI.\n\n\"Mr. Jensen Huang was appreciative of the strides India has made in this sector and was equally upbeat about the talented youth of India,\" the prime minister said.\n\nNvidia Corporation is an American multinational technology company that was founded April 5, 1993, by Jensen Huang, Chris Malachowsky, and Curtis Priem, with a vision to bring 3D graphics to the gaming and multimedia markets.",
                    "PM Modi meets Nvidia chief Jensen Huang.New Delhi, Sep 4 (SocialNews.XYZ) Prime Minister Narendra Modi on Monday met CEO of Nvidia Jensen Huang.\n\n\"Had an excellent meeting with Jensen Huang, the CEO of @nvidia. We talked at length about the rich potential India offers in the world of AI. Jensen Huang was appreciative of the strides India has made in this sector and was equally upbeat about the talented youth of India,\" PM Modi posted on X, formerly Twitter, after the meeting.\n\nNvidia Corporation is an American multinational technology company, which designs graphics processing units and application programming interface for data science and high performance computing.",
                    "Starfield's most downloaded PC mod so far is the one that replaces AMD FSR with NVIDIA DLSS.Bethesda Game Studios RPGs and mods go hand-in-hand, especially when looking at the developer's history in the PC gaming space - Morrowing, Oblivion, Skyrim, and most recently, Fallout 4. Some of the most moddable and modded games of all time, from simple texture updates to visual overhauls, redesigned UI, and even brand-new games.\n\nStarfield will follow suit, thanks to the epic space RPG being built with the next iteration of the Creation Engine. Ahead of the launch of official mod kits and tools, as we saw with Fallout 4, based on the modding community's familiarity with the Creation Engine, we're already starting to see several Starfield mods over on Nexus Mods.\n\nAs of writing, the top mods are all about performance, with the number one mod for Starfield at launch being the 'Starfield Upscaler,' which replaces AMD FSR 2 with DLSS or XeSS. It's a straightforward installation that requires FSR 2 to be enabled and then brings up a menu in-game to override AMD's tech with either NVIDIA's or Intel's.\n\nAnd if you're wondering what's the difference, well, DLSS 3.5 in Starfield looks noticeably better than AMD's FSR 2.2 implementation - and even cleans up the image compared to native rendering. The video above showcases some differences, where objects in the background are more stable and don't shimmer or glitch with DLSS.\n\nIn motion, it's a smoother and cleaner presentation, so here's hoping Bethesda adds native DLSS support into the game; otherwise, Starfield Upscaler will remain one of the most popular mods for the game going forward. Other popular Starfield mods at launch include general performance optimization mods and another essential mod for PC gamers - Starfield FOV, which allows you to change the FOV in-game.",
                    "PM Modi, Nvidia CEO discuss India's rich potential in artificial intelligence.New Delhi [India], September 4 (ANI): Prime Minister Narendra Modi on Monday held a meeting with Nvidia CEO Jensen Huang. PM Modi and Huang spoke at length regarding the rich potential India offers in the artificial intelligence sector.\n\nIn a post shared on X, formerly known as Twitter, PM Modi noted that Jensen Huang appreciated strides made by India in the artificial intelligence sector.\n\nPM Modi in a post on X wrote, \"Had an excellent meeting with Mr. Jensen Huang, the CEO of @nvidia. We talked at length about the rich potential India offers in the world of AI. Mr. Jensen Huang was appreciative of the strides India has made in this sector and was equally upbeat about the talented youth of India.\"\n\nUS-based techology company Nvidia was founded by Jansen Huang in 1993. Since its inception, Jansen Huang has served as its chief executive officer, and a member of the board of directors, according to the company statement.\n\nEarlier in June, PM Modi stressed on the role of G20 nations in striking the right balance between the opportunities and challenges posed by digital technology, which he termed as a force multiplier in increasing access to education and adapting to future needs.\n\nWhile addressing a G20 Education Ministers' Meeting held in Pune via video message, PM Modi touched upon the potential of Artificial Intelligence which offers great potential in the field of learning, skilling and education.\n\nThe Prime Minister stressed that G20 countries with their respective strengths can play a crucial role in promoting research and innovation, especially in the Global South. He urged the dignitaries to create a path for increased research collaborations.\n\nPM Modi said that continuous skilling, re-skilling, and up-skilling are key to making youth future-ready, noting that education is not only the foundation upon which India's civilization has been built, but is also the architect of humanity's future.\n\nThrowing light on the emphasis laid on research and innovation, the Prime Minister highlighted that India has set up ten thousand 'Atal Tinkering Labs' across the country which act as research and innovation nurseries for our school children. He informed that more than 7.5 million students are working on more than 1.2 million innovative projects in these labs. (ANI)"
                    ]


def articles_summarizer(article_contents):
    summaries = []
    for content in article_contents:
        prompt = f"Provide a concise summary for the following news article:\n\n{content}"
        response = openai.Completion.create(
        model="text-davinci-003",  # or another suitable model
        prompt=prompt,
        max_tokens=150  # Adjust based on the length you want
        )
        summaries.append(response.choices[0].text.strip())
        print(response.choices[0].text.strip())
        print("xxxxxxxxxxxxxxxxxxxx")
    
    combined_content = "\nArticle Summary:\n" + "\nArticle Summary:\n".join(summaries)
    prompt = f"Each of these is a summary of the top news for Nvidia over the last day , please provide a high-level summary for Nvidia over the last day:\n\n{combined_content}"
    print(prompt)
    print("yyyyyyyyyyyyyyyyyyyyyyy")
    response = openai.Completion.create(
        model="text-davinci-003",  # or another suitable model
        prompt=prompt,
        max_tokens=300  # Adjust based on the length you want
    )
    final_overall_summary = response.choices[0].text.strip()
    print("overall summary")
    print("===============================")
    print(final_overall_summary)

articles_summarizer(article_contents)

due_alerts = Alert.query.filter_by(next_due_date=date.today()).all()
print(due_alerts)

