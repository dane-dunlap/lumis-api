from datetime import datetime, timedelta, date
import requests
import json
from dotenv import load_dotenv
import os



load_dotenv()


news_api_key = os.environ.get('NEWS_API_KEY')
news_api_endpoint = "http://eventregistry.org/api/v1/article/getArticles"
company_name = '"'+ "Nvidia" + '"'
def fetch_articles_for_alert():
    params = {
  "action": "getArticles",
  "keyword": company_name,
  "articlesPage": 1,
  #"conceptURI":"https://en.wikipedia.org/wiki/Nvidia",
  "eventFilter": "skipArticlesWithoutEvent",
  "keywordLoc": "title",
  "articlesCount": 5,
  "lang": "eng",
  "dateStart": date.today() - timedelta(days=1), 
  "dateEnd": date.today(),
  "articlesSortBy": "sourceImportanceRank",
  "articlesArticleBodyLen": -1,
  "resultType": "articles",
  "dataType": [
    "news",
    "pr"
  ],
  "apiKey": news_api_key,
  "forceMaxDataTimeWindow": 31
}

    response = requests.get(news_api_endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error": response.status_code, "Message": response.text}



response_data = fetch_articles_for_alert()
json_string = json.dumps(response_data, indent=4)
print("===================================")
print(company_name)
print(json_string)


