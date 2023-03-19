import requests
from datetime import date
from datetime import timedelta
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
STOCK = "AMZN"
COMPANY_NAME = "Amazon.com, Inc."
sending_msg = False
## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").


# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
stock_parameters={
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": "AQN12VBW8O41GDJW",
}
stock_url = 'https://www.alphavantage.co/query'
stock_response = requests.get(stock_url, params=stock_parameters)

stock_data = stock_response.json()
today = date.today()
# print(today)
# Yesterday date
yesterday = today - timedelta(days = 2)
yesterday_before_today = today - timedelta(days = 3)

ending_hour = 20
yesterday_time = datetime(yesterday.year, yesterday.month, yesterday.day, ending_hour)
# print(yesterday_time)
yesterday_before_today_time = datetime(yesterday_before_today.year, yesterday_before_today.month, yesterday_before_today.day, ending_hour)
# print(yesterday_before_today_time)

yesterday_closes_at = stock_data["Time Series (60min)"][str(yesterday_time)]["4. close"]
yesterday_before_today_time_closes_at = stock_data["Time Series (60min)"][str(yesterday_before_today_time)]["4. close"]
# print(yesterday_closes_at)
# print(yesterday_before_today_time_closes_at)

delta_difference = float( 1 - ( float(yesterday_before_today_time_closes_at) / float(yesterday_closes_at) ) ) * 100
# print(delta_difference)
if delta_difference < -1 or delta_difference > 1:
    sending_msg = True

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
if sending_msg:
    print("Sending Message...")
    news_parameters={
        "q": COMPANY_NAME,
        "from": str(yesterday),
        "sortBy": "popularity",
        "apiKey": "00d177571d0d42578aca8b83eb708cd3",
    }
    news_url = ('https://newsapi.org/v2/everything')

    news_response = requests.get(news_url, params=news_parameters)

    # print(news_response.json())
    news_data = news_response.json()

    required_news = []
    # print(news_data)
    # print(required_news)
    for news in news_data["articles"][0:3]:
        required_news.append({
            "title": news["title"],
            "description": news["description"],
            "url": news["url"],
        })
    # print(required_news)
    ## STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number. 

    msg_body = ""
    for news in required_news:
        msg_body += f"Headline: {news['title']}\nBrief: {news['description']}\n"
        
    msg_body += f"------\nAttachments:\n"

    for news in required_news:
        msg_body += f"{news['url']}\n"
    
    account_sid = os.getenv('ACOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    # print(auth_token)
    client = Client(account_sid, auth_token)

    if delta_difference > 0:
        message = client.messages.create(
        body=f"""\n
        {COMPANY_NAME}: 🔼 {str(round(delta_difference, 2))}%
        {msg_body}
            """,
        from_="+15074739989",
        to="+201207551921"
        )
    else:
        
        message = client.messages.create(
        body=f"""\n
        {COMPANY_NAME}: 🔼 {str(round(delta_difference, 2))}%
        {msg_body}
            """,
        from_="+15074739989",
        to="+201207551921"
        )
    print(message.sid)

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

