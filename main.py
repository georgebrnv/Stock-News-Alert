import requests
from datetime import *
import smtplib
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API")

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API")

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("EMAIL_TEMP_PASS")

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}

news_parameters = {
    "apiKey": NEWS_API_KEY,
    "q": COMPANY_NAME,
    "language": "en",
    "page": 1,
    "pageSize": 3
}
# Keep hold of yesterday and before yesterday dates
current_date = datetime.now()
yesterday = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
before_yesterday = (current_date - timedelta(days=2)).strftime("%Y-%m-%d")

delta_price = 0


def stock_price_check():

    # Request data (json format)
    stock_response = (requests.get(STOCK_ENDPOINT, stock_parameters)).json()
    print(stock_response)
    # Keep hold of closing prices
    yesterday_closing_price = float(stock_response["Time Series (Daily)"][yesterday]["4. close"])
    before_yesterday_closing_price = float(stock_response["Time Series (Daily)"][before_yesterday]["4. close"])
    print(yesterday_closing_price, before_yesterday_closing_price)

    # Price change
    delta_price = abs((yesterday_closing_price - before_yesterday_closing_price) / before_yesterday_closing_price * 100)
    print(f"Price change: {round(delta_price, 2)}.")

    if delta_price > 5:
        news_check()
    else:
        print("Price hasn't changed a lot.")


def news_check():
    news_dic = {}
    news_response = requests.get(NEWS_ENDPOINT, news_parameters)
    for index, news in enumerate(news_response.json()["articles"]):
        title = news["title"]
        main_part = news["description"]
        news_dic[str(index + 1)] = {"title": title, "main_part": main_part}
    send_email(news_dic)


def send_email(dictionary):
    connection = smtplib.SMTP("smtp.mail.ru")
    connection.starttls()
    connection.login(user=EMAIL, password=PASSWORD)
    connection.sendmail(
        from_addr=EMAIL,
        to_addrs=EMAIL,
        msg=f"Subject: TSLA +{delta_price}\n\n"
            f"{dictionary['1']['title']}\n {dictionary['1']['main_part']}\n"
            f"{dictionary['2']['title']}\n {dictionary['2']['main_part']}\n"
            f"{dictionary['3']['title']}\n {dictionary['3']['main_part']}\n"
    )


stock_price_check()

