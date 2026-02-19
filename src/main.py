from datetime import datetime

import requests
from tinydb import TinyDB

from src import config
from src.logger import logger

db = TinyDB(config.DB_PATH)


def get_price() -> dict | None:
    """
    Busca o preço atual do Bitcoin em USD na API da Coinbase.

    Define um timeout de 5 segundos e trata exceções de conexão,
    timeout e outras exceções de requisição HTTP.

    Returns:
        dict: Os dados de preço em formato JSON, ou None em caso de erro.
    """
    logger.info("Iniciando busca de preço na API da Coinbase.")
    try:
        url = f"{config.API_URL}?currency={config.CURRENCY}"
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()  # Levanta um erro para respostas 4xx/5xx
        price_data = response.json()
        logger.info(f"Preço obtido com sucesso: {price_data}")
        return price_data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão ao buscar preço: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout ao buscar preço: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição ao buscar preço: {e}")
        return None


def calculate_kpis(price_data: dict) -> dict | None:
    """
    Calcula os KPIs (Key Performance Indicators) a partir dos dados de preço.

    Args:
        price_data (dict): Dicionário contendo os dados de preço da API.
                           Ex: {'data': {'amount': '50000.00'}}

    Returns:
        dict: Um dicionário com price_usd, price_real e timestamp.
              Retorna None em caso de dados inválidos ou erro.
    """
    logger.info("Iniciando cálculo de KPIs.")
    if not price_data:
        logger.error("Erro: price_data está vazio.")
        return None

    if "data" not in price_data or "amount" not in price_data.get("data", {}):
        logger.error(f"Erro: Estrutura de dados inválida em price_data: {price_data}")
        return None

    try:
        price_usd = float(price_data["data"]["amount"])
        price_real = price_usd * config.USD_TO_BRL_RATE
        logger.info(f"Convertendo ${price_usd} para R$ {price_real}")
        kpis = {
            "price_usd": price_usd,
            "price_real": price_real,
            "timestamp": datetime.now().isoformat(),
        }
        logger.debug(f"KPIs calculados: {kpis}")
        return kpis
    except ValueError:
        logger.error(
            f"Erro: 'amount' não é um número válido: {price_data['data']['amount']}"
        )
        return None


def save_kpis_to_db(kpis: dict) -> None:
    """Salva os KPIs no banco de dados TinyDB."""
    logger.info("Iniciando salvamento no banco de dados.")
    if kpis:
        db.insert(kpis)
        logger.info(f"Registro salvo no DB: {kpis}")
    else:
        logger.error("Nenhum KPI para salvar.")


def main() -> None:
    """Função principal para orquestrar o ETL."""
    logger.info("--- Iniciando pipeline de ETL de Preço do Bitcoin ---")
    price_data = get_price()
    kpis = calculate_kpis(price_data)
    save_kpis_to_db(kpis)
    logger.info("--- Pipeline de ETL finalizado ---")


if __name__ == "__main__":
    main()
