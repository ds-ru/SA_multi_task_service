from app_pages.page_main import render as home_page
from app_pages.page_api import render as api_stats_page
from app_pages.page_magnetto import render as magnetto_page
from app_pages.page_obj_storage import render as object_storage_page
from app_pages.page_decline_ads import render as decline_ads_page
from app_pages.page_dbs_check import render as dbs_check_page

PAGES = {
    "Главная": home_page,
    "Сверка статистики API + Загрузка бенчей": api_stats_page,
    "Сверка статистики Magnetto": magnetto_page,
    "Работа с объектным хранилищем": object_storage_page,
    "Полное отклонение кабинета": decline_ads_page,
    "Проверка текущей статистики по базам": dbs_check_page,
}