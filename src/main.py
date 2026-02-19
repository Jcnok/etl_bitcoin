import requests 
from tinydb import TinyDB
from datetime import datetime

db = TinyDB('db.json')

def get_price():
    """
    Busca o preço atual do Bitcoin em USD na API da Coinbase.

    Define um timeout de 5 segundos e trata exceções de conexão,
    timeout e outras exceções de requisição HTTP.

    Returns:
        dict: Os dados de preço em formato JSON, ou None em caso de erro.
    """
    try:
        url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Levanta um erro para respostas 4xx/5xx
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Erro de conexão ao buscar preço: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Timeout ao buscar preço: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao buscar preço: {e}")
        return None

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
