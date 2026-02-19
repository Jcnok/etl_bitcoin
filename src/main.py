import requests 
from tinydb import TinyDB, Query
from datetime import datetime

db = TinyDB('db.json')

def get_price():
  url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
  response = requests.get(url)
  return response.json()

def calculate_kpis(price_data):
  price_usd = price_data['data']['amount']
  price_real = float(price_usd)* 5.5
  price_data['price_real']