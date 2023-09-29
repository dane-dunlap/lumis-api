from app_store_scraper import AppStore
import ast
from pprint import pprint



stake = AppStore(country="us", app_name="arrived-real-estate-investing",app_id=1603728735)
stake.review(how_many=5000)

print(stake)






