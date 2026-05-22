from sqlalchemy import create_engine, text

from config.service import DB_URL_CONNECT
from config.logger import logger

try:
    engine = create_engine(url=DB_URL_CONNECT)

    with engine.connect() as conn:
        a = conn.execute(text('SELECT version()'))

        logger.info(f'Connection DB successfully.\nVersion - {a.fetchall()[0][0]}')

except Exception as e:
    logger.error(f'Не удалось подключится к БД | {type(e).__name__} - {e}')
