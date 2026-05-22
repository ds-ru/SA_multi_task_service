from io import BytesIO

from db_conn.ch_conn import client
from monthly_reports.main import MonthlyReport


class MonthlyReportCH(MonthlyReport):
    async def export_ch_bench(self):
        query = """
            INSERT INTO schema.bench_temp (
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
            )
            SELECT DISTINCT
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
            FROM schema.account_report ar FINAL
            INNER JOIN schema.ads_list al FINAL
                ON ar.account_id = al.account_id AND ar.ad_id::int = al.ad_id::int
            LEFT JOIN schema.account_info ai
                ON ar.account_id = ai.account_id
            WHERE ar.`month` = 12 
              AND ar.`year` = 2025
              AND ai.country_placement = 'Россия';
            """

        export_query = f"""
            SELECT DISTINCT
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
            FROM schema.account_report ar FINAL
            INNER JOIN schema.account_list acl FINAL ON acl.account_id = ar.account_id
            INNER JOIN schema.ads_list al FINAL
                ON ar.account_id = al.account_id AND ar.ad_id::int = al.ad_id::int
            LEFT JOIN schema.account_info ai
                ON ar.account_id = ai.account_id
            WHERE ar.`month` = {self.prev_month}
              AND ar.`year` = {self.prev_year}
              AND ai.country_placement = 'Россия'
        """

        df = client.query_df(export_query)
        df = await self._drop_tz(df)
        print(f"Получено строк: {len(df):,}")

        # === Убираем временные зоны (если есть datetime-колонки) ===
        df = await self._drop_tz(df)

        # === Удаляем дубли внутри каждой "партиции" по account_id ===
        df = (
            df.sort_values(["account_id", "ad_id"])  # сортировка для стабильности
            .drop_duplicates(subset=["account_id", "ad_id"], keep="last")  # оставляем последнюю запись
            .reset_index(drop=True)
        )
        print(f"После удаления дублей: {len(df):,} строк")
        # df.to_excel(f"export_CH_bench.xlsx", index=False)

        try:
            # Важно: порядок колонок должен совпадать с определением таблицы mart.bench_temp
            insert_cols = [
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
            ]

            # Переименуем поля, чтобы совпадали с тем, как в таблице:
            df = df.rename(
                columns={
                    "target_languages": "target_languages_language_code",
                    "target_topics": "target_topics_name",
                    "target_exclude_topics": "target_exclude_topics_name",
                    "device": "target_device",
                }
            )

            # Переупорядочим колонки точно под структуру таблицы
            df = df[
                [
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                ]
            ]

            print(f"Получено строк: {len(df):,}")
            df = await self._drop_tz(df)

            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            file_name = f"CH_bench_{self.start_prev_month}--{self.end_prev_month}.xlsx"

        except Exception as e:
            print(f"Ошибка вставки в ClickHouse: {e}")
            raise

        return file_name, buffer

    async def export_ch_PLACEHOLDER(self):
        query = f"""
        with ads as (
    	select
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
    	from schema.ads_list al final
        ),
        accounts as (
            SELECT account_id, any(title) AS account_title
            FROM schema.account_list
            WHERE title LIKE '%PLACEHOLDER%'
            GROUP BY account_id
        ),
        stats as (
            select
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
                xxxx,
            from
                schema.account_report ar final
            where
                "month" = {self.prev_month} AND "year" = {self.prev_year}
            AND
            ar.account_id IN 
                (SELECT 
                    account_id 
                FROM 
                    schema.account_list final
                WHERE title LIKE '%PLACEHOLDER%')
            group by
                1,2
        )
        select
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
            xxxx,
        from  stats as2
        left join accounts cc 
            ON as2.account_id = cc.account_id
        left join ads a
            on as2.account_id = a.account_id and as2.ad_id = a.ad_id
        """
        df = client.query_df(query)
        df = await self._drop_tz(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        file_name = f"PLACEHOLDER_api_closing_{self.start_prev_month}--{self.end_prev_month}.xlsx"

        return file_name, buffer

    async def insert_bench(self):
        query = f"""
                INSERT INTO schema.bench_temp (
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                )
                SELECT DISTINCT
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                FROM schema.account_report ar FINAL
                INNER JOIN schema.ads_list al FINAL
                    ON ar.account_id = al.account_id AND ar.ad_id::int = al.ad_id::int
                LEFT JOIN schema.account_info ai
                    ON ar.account_id = ai.account_id
                WHERE ar.`month` = {self.prev_month} 
                  AND ar.`year` = {self.prev_year}
                  AND ai.country_placement = 'Россия';
                """
        client.command(query)
        client.command("OPTIMIZE TABLE schema.bench_temp FINAL")
        return True