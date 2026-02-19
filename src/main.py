import argparse
import os
from datetime import datetime

import requests
from tinydb import TinyDB

from src import cli, config
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


def get_usd_to_brl_rate() -> float | None:
    """
    Busca a cotação atual de USD para BRL de uma API externa.

    Returns:
        float: A cotação de USD para BRL, ou None em caso de erro.
    """
    logger.info("Iniciando busca da cotação USD->BRL.")
    try:
        response = requests.get(
            config.EXCHANGE_RATE_API_URL, timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        rate = float(data["rates"]["BRL"])
        logger.info(f"Cotação USD->BRL obtida com sucesso: {rate}")
        return rate
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        logger.error(f"Erro ao buscar cotação USD->BRL: {e}")
        return None


def calculate_kpis(price_data: dict, usd_to_brl_rate: float) -> dict | None:
    """
    Calcula os KPIs (Key Performance Indicators) a partir dos dados de preço.

    Args:
        price_data (dict): Dicionário contendo os dados de preço da API.
                           Ex: {'data': {'amount': '50000.00'}}
        usd_to_brl_rate (float): A cotação atual de USD para BRL.

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
        price_real = price_usd * usd_to_brl_rate
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


def run_etl_pipeline() -> None:
    """Função que executa o pipeline de ETL uma vez."""
    logger.info("--- Iniciando pipeline de ETL de Preço do Bitcoin ---")

    # Busca a cotação do dólar, com fallback para o valor configurado
    usd_to_brl_rate = get_usd_to_brl_rate()
    if not usd_to_brl_rate:
        usd_to_brl_rate = config.FALLBACK_USD_TO_BRL_RATE
        logger.warning(
            f"Falha ao buscar cotação. Usando valor de fallback: {usd_to_brl_rate}"
        )

    price_data = get_price()
    kpis = calculate_kpis(price_data, usd_to_brl_rate)
    save_kpis_to_db(kpis)
    logger.info("--- Pipeline de ETL finalizado ---")


def main() -> None:
    """
    Função principal que controla a CLI.
    """
    parser = argparse.ArgumentParser(
        description="ETL de Preços de Bitcoin com agendamento e análise."
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Comandos disponíveis", required=True
    )

    # Comando 'fetch'
    subparsers.add_parser(
        "fetch", help="Busca o preço mais recente e salva no banco de dados."
    )

    # Comando 'schedule'
    subparsers.add_parser(
        "schedule", help="Executa o ETL continuamente em intervalos agendados."
    )

    # Comando 'history'
    subparsers.add_parser("history", help="Mostra os últimos 10 registros de preço.")

    # Comando 'stats'
    subparsers.add_parser(
        "stats", help="Exibe estatísticas (mín, máx, média) dos preços registrados."
    )

    # Comando 'export'
    export_parser = subparsers.add_parser("export", help="Exporta os dados de preço.")
    export_parser.add_argument(
        "--format",
        choices=["csv", "json"],
        required=True,
        help="O formato do arquivo de exportação (csv ou json).",
    )
    export_parser.add_argument(
        "--output",
        default=None,
        help="O nome do arquivo de saída. Padrão: prices.csv ou prices.json.",
    )

    args = parser.parse_args()

    if args.command == "fetch":
        run_etl_pipeline()
    elif args.command == "schedule":
        # Import local para evitar dependência circular
        from src import scheduler

        scheduler.start()
    elif args.command == "history":
        cli.show_history()
    elif args.command == "stats":
        cli.show_stats()
    elif args.command == "export":
        # Garante que o diretório de saída exista
        output_dir = "db"
        os.makedirs(output_dir, exist_ok=True)

        if args.format == "csv":
            filename = args.output or "prices.csv"
            output_path = os.path.join(output_dir, os.path.basename(filename))
            cli.export_to_csv(output_path)
        elif args.format == "json":
            filename = args.output or "prices.json"
            output_path = os.path.join(output_dir, os.path.basename(filename))
            cli.export_to_json(output_path)


if __name__ == "__main__":
    main()
