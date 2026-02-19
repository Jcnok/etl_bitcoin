import csv

from tinydb import TinyDB

from src import config
from src.logger import logger


# ANSI color codes
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    ENDC = "\033[0m"


db = TinyDB(config.DB_PATH)


def show_history() -> None:
    """Mostra os últimos 10 registros de preço do banco de dados."""
    logger.info("Executando comando 'history'.")
    print(f"{Colors.BLUE}--- Últimos 10 Registros de Preço ---{Colors.ENDC}")
    all_records = sorted(db.all(), key=lambda x: x["timestamp"], reverse=True)
    last_10 = all_records[:10]

    if not last_10:
        print(
            f"{Colors.YELLOW}Nenhum registro encontrado no banco de dados.{Colors.ENDC}"
        )
        return

    for record in reversed(last_10):
        print(
            f"[{record['timestamp']}] USD: ${record['price_usd']:.2f} | "
            f"BRL: R${record['price_real']:.2f}"
        )


def show_stats() -> None:
    """Calcula e exibe estatísticas sobre os preços armazenados."""
    logger.info("Executando comando 'stats'.")
    print(f"{Colors.BLUE}--- Estatísticas de Preço (USD) ---{Colors.ENDC}")
    all_records = db.all()

    if not all_records:
        print(
            f"{Colors.YELLOW}Nenhum registro para calcular estatísticas.{Colors.ENDC}"
        )
        return

    prices_usd = [rec["price_usd"] for rec in all_records]

    avg_price = sum(prices_usd) / len(prices_usd)
    min_price = min(prices_usd)
    max_price = max(prices_usd)

    print(f"Registros totais: {len(prices_usd)}")
    print(f"Preço Médio: {Colors.GREEN}${avg_price:.2f}{Colors.ENDC}")
    print(f"Preço Mínimo: {Colors.YELLOW}${min_price:.2f}{Colors.ENDC}")
    print(f"Preço Máximo: {Colors.RED}${max_price:.2f}{Colors.ENDC}")


def export_to_csv() -> None:
    """Exporta todos os dados de preço para um arquivo CSV."""
    logger.info("Executando comando 'export --csv'.")
    all_records = db.all()
    if not all_records:
        logger.warning("Nenhum registro encontrado para exportar.")
        print(f"{Colors.YELLOW}Nenhum registro para exportar.{Colors.ENDC}")
        return

    filename = "prices.csv"
    try:
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["timestamp", "price_usd", "price_real"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in sorted(all_records, key=lambda x: x["timestamp"]):
                writer.writerow(
                    {
                        "timestamp": record["timestamp"],
                        "price_usd": record["price_usd"],
                        "price_real": record["price_real"],
                    }
                )
        logger.info(f"Dados exportados com sucesso para {filename}")
        print(
            f"{Colors.GREEN}Dados exportados com sucesso para {filename}{Colors.ENDC}"
        )
    except IOError as e:
        logger.error(f"Erro ao escrever no arquivo {filename}: {e}")
        print(f"{Colors.RED}Erro ao escrever no arquivo {filename}: {e}{Colors.ENDC}")
