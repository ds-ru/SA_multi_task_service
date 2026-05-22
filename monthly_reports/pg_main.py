from io import BytesIO

import pandas as pd
from sqlalchemy import text

from db_conn.pg_conn import engine
from monthly_reports.main import MonthlyReport


class MonthlyReportPG(MonthlyReport):
    async def export_pg(self):
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
                from schema.ads_list al 
            ),
            ad_stat as (
                select
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                    xxxx,
                from schema.ad_stats as2 
                where effective_date between '{self.start_prev_month}' and '{self.end_prev_month}'
                group by 1,2
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
                    schema.account_report ar 
                join 
                    schema.related_accounts ra 
                on 
                    ar.account_id = ra.account_id 
                where 
                    "month" = '{self.start_prev_month}'  -- format 'YYYY-MM-DD'
                    and
                    ra.main_account in ('PLACEHOLDER', 'PLACEHOLDER', 'PLACEHOLDER')
                    and
                    ra.account_title like '%PLACEHOLDER%'
                group by
                    1,2,3
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
                (as2.actions * 1.0 / NULLIF(as2.views, 0)) as cr,
                (as2.spent_budget / NULLIF(as2.actions, 0)) as cpa,
                (as2.spent_budget / NULLIF(as2.clicks, 0)) as cpc,
                ((as2.spent_budget / NULLIF(as2.views, 0)) * 1000) as cpm
            from  stats s
            left join ads a
                on s.account_id = a.account_id and s.ad_id = a.ad_id
            left join ad_stat as2
                on s.account_id = as2.account_id and s.ad_id = as2.ad_id;
        """

        df = pd.read_sql(text(query), con=engine)
        df = await self._drop_tz(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        file_name = f"PLACEHOLDER_magnetto_closing_{self.start_prev_month}--{self.end_prev_month}.xlsx"

        return file_name, buffer
