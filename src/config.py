import os

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da API
API_URL = os.getenv("API_URL", "https://api.coinbase.com/v2/prices/spot")
CURRENCY = os.getenv("CURRENCY", "USD")

# Configurações de processamento de dados
try:
    # Define uma cotação de fallback caso a API falhe
    FALLBACK_USD_TO_BRL_RATE = float(os.getenv("FALLBACK_USD_TO_BRL_RATE", "5.5"))
except ValueError:
    print("Aviso: FALLBACK_USD_TO_BRL_RATE não é um float válido. Usando o padrão 5.5.")
    FALLBACK_USD_TO_BRL_RATE = 5.5

# URL da API de cotação de moeda
EXCHANGE_RATE_API_URL = os.getenv(
    "EXCHANGE_RATE_API_URL", "https://api.exchangerate-api.com/v4/latest/USD"
)

# Configurações de Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configurações do Banco de Dados
DB_PATH = os.getenv("DB_PATH", "db.json")

# Configurações de Requisição
try:
    # Converte o timeout para inteiro
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
except ValueError:
    print("Aviso: REQUEST_TIMEOUT não é um inteiro válido. Usando o padrão 5.")
    REQUEST_TIMEOUT = 5

# Configurações do Agendador
try:
    # Converte o intervalo do agendador para inteiro
    SCHEDULE_MINUTES = int(os.getenv("SCHEDULE_MINUTES", "5"))
except ValueError:
    print("Aviso: SCHEDULE_MINUTES não é um inteiro válido. Usando o padrão 5.")
    SCHEDULE_MINUTES = 5
