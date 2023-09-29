from itunes_app_scraper.scraper import AppStoreScraper

scraper = AppStoreScraper()
results = scraper.get_app_ids_for_query("Stake | Property Investing")

#app_details = scraper.get_app_details(results,"ae",add_ratings=True)

app_details = scraper.get_app_details(results[0])

print(app_details)
#print(list(app_details))


#scraper = AppStoreScraper()
#results = scraper.get_app_ids_for_query("fortnite")
#similar = scraper.get_similar_app_ids_for_app(results[0])

#app_details = scraper.get_multiple_app_details(similar)
#ssprint(list(app_details))