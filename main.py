import requests
import os
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

FROM_NUM = os.environ["FROM_NUM"]
TO_NUM = os.environ["TO_NUM"]

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

alpha_vantage_api_key = os.environ["AV_API_KEY"]
news_api = os.environ["NEWS_API"]

account_sid = os.environ["ACCOUNT_SID"]
auth_token = os.environ["AUTH_TOKEN"]

alpha_vantage_params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': alpha_vantage_api_key,
}

news_api_params = {
    'apiKey': news_api,
    'qInTitle': COMPANY_NAME,
}

# Making the get request
response = requests.get(url=STOCK_ENDPOINT, params=alpha_vantage_params)
response.raise_for_status()
stock_data = response.json()["Time Series (Daily)"]

# Getting yesterday's closing stock price
data_list = [value for (key, value) in stock_data.items()]
yesterday_data = data_list[0]
yesterday_close = float(yesterday_data['4. close'])

# Getting the day before yesterday's closing stock price
day_before_yesterday = data_list[1]
day_before_yesterday_close = float(day_before_yesterday['4. close'])

# Finding the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20.
positive_diff = yesterday_close - day_before_yesterday_close
positive_difference = abs(positive_diff)

up_down = None
up_down = '🔺' if positive_diff > 0 else '🔻'

# Working out the percentage difference in price between closing price yesterday and closing price the day
# before yesterday.
diff_percent = (positive_difference / yesterday_close) * 100

# Using the News API to get the first 3 news articles related to the COMPANY_NAME.
if diff_percent > 0:
    response_2 = requests.get(url=NEWS_ENDPOINT, params=news_api_params)
    response.raise_for_status()
    articles = response_2.json()['articles']

    # Creating a list that contains the first 3 articles
    top_3_articles = articles[:3]

    # Creating a new list of the first 3 article's headline and description.
    formatted_articles = [
        f"{STOCK_NAME}:{up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for
        article in top_3_articles]

    # Sending each article as a separate message via Twilio.
    client = Client(account_sid, auth_token)

    for articles in formatted_articles:
        message = client.messages \
            .create(
            body=articles,
            from_=FROM_NUM,
            to=TO_NUM
        )
