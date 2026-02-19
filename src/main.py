import requests 
from tinydb import TinyDB, Query
from datetime import datetime

db = TinyDB('db.json')

def get_price():
  url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
  response = requests.get(url)
  return response.json()

def calculate_kpis(price_data):
    """
    Calcula os KPIs (Key Performance Indicators) a partir dos dados de preço.

    Args:
        price_data (dict): Dicionário contendo os dados de preço da API.
                           Ex: {'data': {'amount': '50000.00'}}

    Returns:
        dict: Um dicionário com price_usd, price_real e timestamp.
              Retorna um dicionário vazio em caso de erro de chave (KeyError).
    """
    try:
        price_usd = float(price_data['data']['amount'])
        price_real = price_usd * 5.5  # Cotação fixa para exemplo
        return {
            'price_usd': price_usd,
            'price_real': price_real,
            'timestamp': datetime.now().isoformat()
        }
    except KeyError:
        return {}
