import time

import schedule

from src import config
from src.logger import logger
from src.main import run_etl_pipeline


def schedule_price_check() -> None:
    """
    Job agendado que executa o pipeline de ETL.
    Encapsula a lógica principal para ser chamada pelo agendador.
    """
    logger.info("Executando job agendado: verificação de preço.")
    run_etl_pipeline()


def start() -> None:
    """Inicia o agendador para rodar o job no intervalo configurado."""
    logger.info(
        f"Agendando a execução do job a cada {config.SCHEDULE_MINUTES} minutos."
    )
    schedule.every(config.SCHEDULE_MINUTES).minutes.do(schedule_price_check)

    logger.info("Agendador iniciado. Pressione Ctrl+C para sair.")
    while True:
        schedule.run_pending()
        time.sleep(1)
