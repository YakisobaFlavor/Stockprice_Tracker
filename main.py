import requests
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv("apikey.env") # Storage for your important apikey

# Your Twilio important info save in .env file
VIRTUAL_TWILIO_NUMBER = os.getenv("VIRTUAL_TWILIO_NUMBER")
VERIFIED_NUMBER = os.getenv("VERIFIED_NUMBER") 
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Lookup particular company's stock price using AlphaVantage API
STOCK_NAME = "COMPANY STOCK CODE"
COMPANY_NAME = "COMPANY NAME"
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
STOCK_FUNCTION = "TIME_SERIES_DAILY" # For daily stock data
STOCK_ENDPOINT = "https://www.alphavantage.co/query
STOCK_PARAMETERS = {
    "function":STOCK_FUNCTION,
    "symbol":STOCK_NAME,
    "apikey":STOCK_API_KEY,
}

stock_request = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMETERS)
stock_data = stock_request.json()["Time Series (Daily)"]

# Lookup recent news, that may effect stock price fluctuate using NewsAPI
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_QUERIES = COMPANY_NAME
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

current_day = str(date.today())
oldest_day = str(date.today()-timedelta(days=3))

NEWS_PARAMETERS = {
    "Language": "en", # change to another language article default in english
    "q":NEWS_QUERIES,
    "apikey":NEWS_API_KEY,
    "sortBy":"popularity", # sort the article by popularity, default in published date order
    "from": oldest_day,
    "to": current_day,
    }

# Get two previous closing stock data
def get_stock_data_dif(stock_data:dict):
    stock_data_list = [value for (key, value) in stock_data.items()]
    
    yesterday_data = stock_data_list[0]
    yesterday_closing_price = yesterday_data["4. close"] # Key for close price

    yesterday2_data = stock_data_list[1]
    yesterday2_closing_price = yesterday2_data["4. close"] # Key for close price

    difference = float(yesterday_closing_price) - float(yesterday2_closing_price)
    diff_percent = round((difference/float(yesterday_closing_price) * 100), 2)

    if difference > 0:
        up_down = "🔺"
    else:
        up_down = "🔻"
    
    return (up_down, diff_percent)

# Send notification alert and news to your phone whenever price difference more than threshold value
def get_notif(delta_price, up_or_down):  
    if abs(delta_price) > 1: # Threshold for 1% stock price difference, change threshold value as you will
        news_request = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMETERS)
        articles = news_request.json()["articles"]

        #Use Python slice operator to create a list that contains 3 articles
        three_articles = articles[:3]

        formatted_articles = [f"""{STOCK_NAME}: {up_or_down}{delta_price}%\n Headline: {content['title']}.\nBrief: {content['description']}""" for content in three_articles]
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

        for content in formatted_articles:
            message = client.messages.create(
                body=content,
                from_=VIRTUAL_TWILIO_NUMBER,
                to=VERIFIED_NUMBER
            )

up_down_mark, delta_price_percentage = get_stock_data_dif(stock_data)
get_notif(delta_price_percentage, up_down_mark)