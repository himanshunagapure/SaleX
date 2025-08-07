'''
This is example flow

1. First we get customer input
2. We pass that input to Gemini and create multiple relevant queries to search 
3. For each query we run the run web_url_scraper. It collects the urls and save to database
4. Now based on the input which was selected we run respective scrapers.
    a. If user selected instagram we run instagram_scraper.
    b. If user selected linkedin we run linkedin_scraper.
    c. If user selected twitter we run twitter_scraper. etc.
5. Data should be saved to database

'''