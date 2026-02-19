import logging
import sys

# Criar um logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Criar um formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Criar um handler para o arquivo
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Criar um handler para o console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)  # Log INFO e acima para o console
stream_handler.setFormatter(formatter)

# Adicionar os handlers ao logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
