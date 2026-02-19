import csv
import json
from datetime import datetime, timedelta

from tabulate import tabulate
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


def get_history(n: int = 10) -> list[dict]:
    """Busca os últimos N registros de preço do banco de dados."""
    all_records = sorted(db.all(), key=lambda x: x["timestamp"], reverse=True)
    return all_records[:n]


def get_statistics() -> dict | None:
    """Calcula estatísticas dos preços registrados nas últimas 24 horas."""
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    all_records = db.all()
    recent_records = [
        rec
        for rec in all_records
        if datetime.fromisoformat(rec["timestamp"]) >= twenty_four_hours_ago
    ]

    if len(recent_records) < 2:
        return None

    prices_usd = [rec["price_usd"] for rec in recent_records]

    # Ordena por timestamp para calcular a variação corretamente
    recent_records.sort(key=lambda x: x["timestamp"])

    first_price = recent_records[0]["price_usd"]
    last_price = recent_records[-1]["price_usd"]

    variation = (
        ((last_price - first_price) / first_price) * 100 if first_price != 0 else 0
    )

    return {
        "records_count": len(prices_usd),
        "avg_price": sum(prices_usd) / len(prices_usd),
        "min_price": min(prices_usd),
        "max_price": max(prices_usd),
        "variation_24h": variation,
    }


def show_history() -> None:
    """Mostra os últimos 10 registros de preço do banco de dados em uma tabela."""
    logger.info("Executando comando 'history'.")
    history_data = get_history(10)

    if not history_data:
        print(
            f"{Colors.YELLOW}Nenhum registro encontrado no banco de dados.{Colors.ENDC}"
        )
        return

    table_data = [
        [
            record["timestamp"],
            f"${record['price_usd']:,.2f}",
            f"R${record['price_real']:,.2f}",
        ]
        for record in history_data
    ]
    headers = ["Timestamp", "USD", "BRL"]
    print(
        f"\n{Colors.BLUE}╔{'═' * 40}╗\n"
        f"║{'Bitcoin Price History':^40}║\n"
        f"╚{'═' * 40}╝"
        f"{Colors.ENDC}"
    )
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


def show_stats() -> None:
    """Calcula e exibe estatísticas sobre os preços das últimas 24h."""
    logger.info("Executando comando 'stats'.")
    stats = get_statistics()

    if not stats:
        print(
            f"{Colors.YELLOW}Nenhum registro nas últimas 24 horas para calcular estatísticas.{Colors.ENDC}"
        )
        return

    variation_str = f"{stats['variation_24h']:.2f}%"
    color = Colors.GREEN if stats["variation_24h"] >= 0 else Colors.RED
    colored_variation = f"{color}{variation_str}{Colors.ENDC}"

    table_data = [
        ["Registros (24h)", stats["records_count"]],
        ["Preço Médio (USD)", f"${stats['avg_price']:,.2f}"],
        ["Preço Mínimo (USD)", f"${stats['min_price']:,.2f}"],
        ["Preço Máximo (USD)", f"${stats['max_price']:,.2f}"],
        ["Variação (24h)", colored_variation],
    ]

    headers = [f"{Colors.BLUE}Métrica{Colors.ENDC}", f"{Colors.BLUE}Valor{Colors.ENDC}"]
    print(
        f"\n{Colors.BLUE}╔{'═' * 40}╗\n"
        f"║{'Estatísticas (Últimas 24h)':^40}║\n"
        f"╚{'═' * 40}╝{Colors.ENDC}"
    )
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


def export_to_csv(filename: str = "prices.csv") -> None:
    """Exporta todos os dados de preço para um arquivo CSV."""
    logger.info(f"Executando exportação para CSV em '{filename}'.")
    all_records = db.all()
    if not all_records:
        logger.warning("Nenhum registro encontrado para exportar.")
        print(f"{Colors.YELLOW}Nenhum registro para exportar.{Colors.ENDC}")
        return

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
            f"Exportando {len(all_records)} registros para {filename}... {Colors.GREEN}✅{Colors.ENDC}"
        )
    except IOError as e:
        logger.error(f"Erro ao escrever no arquivo {filename}: {e}")
        print(f"{Colors.RED}Erro ao escrever no arquivo {filename}: {e}{Colors.ENDC}")


def export_to_json(filename: str = "prices.json") -> None:
    """Exporta todos os dados de preço para um arquivo JSON."""
    logger.info(f"Executando exportação para JSON em '{filename}'.")
    all_records = db.all()
    if not all_records:
        logger.warning("Nenhum registro encontrado para exportar.")
        print(f"{Colors.YELLOW}Nenhum registro para exportar.{Colors.ENDC}")
        return

    try:
        # Ordena os registros por timestamp para consistência
        sorted_records = sorted(all_records, key=lambda x: x["timestamp"])
        with open(filename, "w") as jsonfile:
            json.dump(sorted_records, jsonfile, indent=4)

        logger.info(f"Dados exportados com sucesso para {filename}")
        print(
            f"Exportando {len(all_records)} registros para {filename}... {Colors.GREEN}✅{Colors.ENDC}"
        )
    except IOError as e:
        logger.error(f"Erro ao escrever no arquivo {filename}: {e}")
        print(f"{Colors.RED}Erro ao escrever no arquivo {filename}: {e}{Colors.ENDC}")
