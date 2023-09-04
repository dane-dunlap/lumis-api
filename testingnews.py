from datetime import datetime, timedelta, date
import requests
import json


NEWS_API_KEY = 'eb9d2fb0-45ba-4081-bc29-1e09413dbbbe'
news_api_endpoint = "http://eventregistry.org/api/v1/article/getArticles"
company_name = '"'+ "Stake Real Estate" + '"'
def fetch_articles_for_alert():
    params = {
  "action": "getArticles",
  "keyword": company_name,
  "articlesPage": 1,
  "conceptURI":"https://en.wikipedia.org/wiki/Nvidia",
  "eventFilter": "skipArticlesWithoutEvent",
  "keywordLoc": "title",
  "articlesCount": 5,
  "lang": "eng",
  "dateStart": date.today() - timedelta(days=24), 
  "dateEnd": date.today(),
  "articlesSortBy": "sourceImportanceRank",
  "articlesArticleBodyLen": 3,
  "resultType": "articles",
  "includeArticleCategories":"True",
  "includeArticleConcepts": "True",
  "dataType": [
    "news",
    "pr"
  ],
  "apiKey": "eb9d2fb0-45ba-4081-bc29-1e09413dbbbe",
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


