import logging
import os
import sys

from src.config import LOG_LEVEL

# Criar um logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Criar um formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Garante que o diretório de logs exista
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "app.log")

# Criar um handler para o arquivo
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Criar um handler para o console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(LOG_LEVEL)  # Usa o nível de log do .env
stream_handler.setFormatter(formatter)

# Adicionar os handlers ao logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
