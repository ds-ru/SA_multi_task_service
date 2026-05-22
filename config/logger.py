import logging

logger = logging.getLogger(__name__)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # ,handlers=[
    #     path,
    #     logging.StreamHandler()
    # ]
)
