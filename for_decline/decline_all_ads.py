import asyncio
from typing import Dict, Any

import aiohttp
import pandas as pd
from config.service import token, URL, proxy
from config.logger import logger


def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def fetch(session: aiohttp.ClientSession, url: str, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    try:
        async with session.get(url=url, params=params, headers=headers, proxy=proxy) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logger.error(f"Fetch error {url}: {e}")
        return {}


async def resolve_account_id(account: str) -> str | None:
    connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=30)

    all_accounts = []
    limit = 10000
    offset = 0

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            query = {
                "limit": limit,
                "offset": offset,
            }

            response = await fetch(
                session=session,
                url=f"{URL}ENDPOINT",
                params=query,
                headers=_get_headers(),
            )

            if not response or "result" not in response:
                return pd.DataFrame()

            batch = response.get("result", {}).get("accounts", [])
            if not batch:
                break

            all_accounts.extend(batch)

            if len(batch) < limit:
                break

            offset += limit

    processed_accounts = []
    for acc in all_accounts:
        processed_accounts.append(
            {
                "account_id": acc.get("account_id"),
                "title": acc.get("title"),
            }
        )

    accounts_df = pd.DataFrame(processed_accounts)

    result = accounts_df[
        accounts_df["title"].astype(str).str.contains(account, case=False, na=False, regex=False)
        |
        (accounts_df["account_id"].astype(str) == str(account))
    ]

    return str(result["account_id"].iloc[0])


async def get_ads_list(account_id) -> pd.DataFrame:
    connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=30)
    account_id = await resolve_account_id(account_id)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        processed_ads = []

        offset = 0
        while True:
            query = {
                "account_id": account_id,
                "offset": offset,
            }

            response = await fetch(
                session=session,
                url=f"{URL}ENDPOINT",
                params=query,
                headers=_get_headers(),
            )

            result = response.get("result", {})
            ads = result.get("ads", [])

            if not ads:
                break

            for ad in ads:
                if ad.get("can_review", False):
                    processed_ads.append(
                        {
                            "account_id": account_id,
                            "ad_id": ad.get("ad_id"),
                            "decline_reason": (ad.get("decline_reason") or {}).get("id"),
                        }
                    )

            offset = result.get("next_offset")
            if offset is None:
                len(processed_ads)
                break

    return pd.DataFrame(processed_ads)


async def decline_ad(
    session: aiohttp.ClientSession,
    ad_id: int,
    decline_reason_id: int,
    account_id: str | None = None,
    return_target: bool = False,
    semaphore: asyncio.Semaphore = 5,
) -> tuple[bool, str]:
    """Возвращает (успех, сообщение_об_ошибке)"""
    async with semaphore:
        payload = {
            "account_id": account_id,
            "ad_id": ad_id,
            "decline_reason_id": decline_reason_id,
            "return_target": return_target,
        }
        try:
            async with session.post(URL + 'ENDPOINT', json=payload, headers=_get_headers(), proxy=proxy) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if data.get("ok"):
                    return True, "OK"
                error_msg = data.get("error", "Unknown error")
                return False, error_msg
        except Exception as e:
            error_msg = str(e)
            logger.error("ENDPOINT ERROR → ad_id={} exception={}", ad_id, error_msg)
            return False, error_msg


async def decline_batch(
    session: aiohttp.ClientSession,
    items: list[tuple[int, str, str, int]],  # (idx, ad_id, account_id, decline_reason_id)
    semaphore: asyncio.Semaphore,
) -> list[tuple[int, bool, str]]:
    """Обрабатывает пакет объявлений параллельно, возвращает [(idx, ok, error), ...]"""
    tasks = [
        decline_ad(session, ad_id, reason_id, account_id, False, semaphore)
        for idx, ad_id, account_id, reason_id in items
    ]
    results = await asyncio.gather(*tasks)
    return [(items[i][0], ok, error) for i, (ok, error) in enumerate(results)]


async def main(account, decline_reason_id):
    account_id = await resolve_account_id(account)

    ads_list = await get_ads_list(account_id)
    ads_list_to_decline = ads_list.copy()
    ads_list_to_decline["decline_status"] = None
    ads_list_to_decline["decline_error"] = None

    logger.info(f"📋 Будет обработано {len(ads_list_to_decline)} уникальных объявлений")

    CONCURRENCY_LIMIT = 30
    BATCH_SIZE = 1_000

    connector = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT, ttl_dns_cache=300)
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with aiohttp.ClientSession(connector=connector, headers=_get_headers()) as session:
        tasks_list = [
            (idx, ad_id, account_id, decline_reason_id)
            for idx, (account_id, ad_id) in enumerate(
                zip(ads_list_to_decline["account_id"], ads_list_to_decline["ad_id"])
            )
        ]

        for batch_start in range(0, len(tasks_list), BATCH_SIZE):
            batch = tasks_list[batch_start:batch_start + BATCH_SIZE]
            batch_end = min(batch_start + BATCH_SIZE, len(tasks_list))

            logger.info(f"🔄 Обработка пакета {batch_start + 1}-{batch_end} из {len(tasks_list)}...")

            results = await decline_batch(session, batch, semaphore)

            for idx, ok, error in results:
                ads_list_to_decline.at[idx, "decline_status"] = "success" if ok else "failed"
                ads_list_to_decline.at[idx, "decline_error"] = None if ok else error

            if batch_end < len(tasks_list):
                await asyncio.sleep(0.1)

    success = int((ads_list_to_decline["decline_status"] == "success").sum())
    failed = int((ads_list_to_decline["decline_status"] == "failed").sum())

    logger.info(f"✅ Готово: {success} успешно, {failed} ошибок")

    failed_df = ads_list_to_decline[ads_list_to_decline["decline_status"] == "failed"].copy()

    return {
        "total": len(ads_list_to_decline),
        "success": success,
        "failed": failed,
        "result_df": ads_list_to_decline,
        "failed_df": failed_df,
    }

if __name__ == "__main__":
    asyncio.run(resolve_account_id("""ACCOUNT_NAME"""))