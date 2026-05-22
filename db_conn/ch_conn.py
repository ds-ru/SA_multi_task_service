import clickhouse_connect
from config.service import CH_HOST, CH_PORT, CH_LOGIN, CH_PWD, CH_SSL_ROOT
from config.logger import logger

try:
    client = clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_LOGIN,
        password=CH_PWD,
        database='schema',
        verify=True, # Сертификат включен
        ca_cert=CH_SSL_ROOT,
    )

    if client.server_version:
        logger.info(f"Connection to {CH_HOST}:{CH_PORT} successfully established.")

except Exception as e:
    logger.error(f'Не удалось подключится к БД | {type(e).__name__} - {e}')
    client = None  # Устанавливаем client в None при ошибке