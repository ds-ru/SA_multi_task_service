from sqlalchemy import text
import pandas as pd
import streamlit as st

from db_conn.pg_conn import engine
from db_conn.ch_conn import client


CACHE_TTL = 600  # 10 минут


@st.cache_data(ttl=CACHE_TTL)
def load_clickhouse_data():
    query = """
    select *
    from schema.ad_stats
    where from_time >= now() - interval 3 day
      and views > 0
    order by from_time desc
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_pg_vitrina():
    query = """
    select *
    from schema.ad_stats_vitrina
    where from_time >= now() - interval '3 day'
      and views > 0
    order by from_time desc
    limit 1000
    """

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


@st.cache_data(ttl=CACHE_TTL)
def load_pg_ad_stats():
    query = """
    select *
    from schema.ad_stats
    where effective_date >= now() - interval '3 day'
      and views > 0
    order by effective_date desc
    limit 1000
    """

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_ad_stats_freshness():
    query = """
    select
        count() as total_rows,
        uniqExact(account_id) as uniq_accounts,
        uniqExact(ad_id) as uniq_ads,
        uniqExact((account_id, ad_id)) as uniq_account_ad_pairs,
        min(from_time) as min_from_time,
        max(from_time) as max_from_time,
        max(to_time) as max_to_time,
        max(load_dttm) as max_load_dttm,
        sum(views) as total_views,
        sum(clicks) as total_clicks,
        sum(actions) as total_actions,
        round(sum(spent_budget), 2) as total_spent_budget
    from schema.ad_stats final
    where from_time >= now() - interval 3 day
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_ad_stats_duplicates():
    query = """
    select
        account_id,
        ad_id,
        from_time,
        count() as cnt,
        min(to_time) as min_to_time,
        max(to_time) as max_to_time,
        min(load_dttm) as min_load_dttm,
        max(load_dttm) as max_load_dttm,
        uniqExact(owner) as uniq_owners,
        sum(views) as sum_views,
        sum(clicks) as sum_clicks,
        sum(actions) as sum_actions,
        round(sum(spent_budget), 2) as sum_spent_budget
    from schema.ad_stats final
    where from_time >= now() - interval 3 day
    group by account_id, ad_id, from_time
    having count() > 1
    order by cnt desc, max_load_dttm desc
    limit 1000
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_ad_stats_anomalies():
    query = """
    select
        account_id,
        ad_id,
        from_time,
        to_time,
        views,
        opens,
        clicks,
        actions,
        spent_budget,
        load_dttm,
        owner,
        multiIf(
            views < 0, 'views < 0',
            opens < 0, 'opens < 0',
            clicks < 0, 'clicks < 0',
            actions < 0, 'actions < 0',
            spent_budget < 0, 'spent_budget < 0',
            clicks > views, 'clicks > views',
            opens > views, 'opens > views',
            actions > views, 'actions > views',
            from_time > to_time, 'from_time > to_time',
            'other'
        ) as anomaly_type
    from schema.ad_stats final
    where from_time >= now() - interval 3 day
      and (
            views < 0
         or opens < 0
         or clicks < 0
         or actions < 0
         or spent_budget < 0
         or clicks > views
         or opens > views
         or actions > views
         or from_time > to_time
      )
    order by from_time desc
    limit 1000
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_ads_list_duplicates():
    query = """
    select
        account_id,
        ad_id,
        count() as cnt,
        min(load_dttm) as min_load_dttm,
        max(load_dttm) as max_load_dttm,
        uniqExact(owner) as uniq_owners,
        uniqExact(status) as uniq_statuses,
        uniqExact(title) as uniq_titles,
        uniqExact(promote_url) as uniq_promote_urls
    from schema.ads_list final
    group by account_id, ad_id
    having count() > 1
    order by cnt desc, max_load_dttm desc
    limit 1000
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_ad_stats_without_ads_list():
    query = """
    select
        s.account_id,
        s.ad_id,
        count() as rows_cnt,
        min(s.from_time) as min_from_time,
        max(s.from_time) as max_from_time,
        max(s.load_dttm) as max_load_dttm,
        sum(s.views) as sum_views,
        sum(s.clicks) as sum_clicks,
        sum(s.actions) as sum_actions,
        round(sum(s.spent_budget), 2) as sum_spent_budget
    from schema.ad_stats s final
    left join schema.ads_list a final
        on s.account_id = a.account_id
       and s.ad_id = a.ad_id
    where s.from_time >= now() - interval 3 day
      and a.ad_id is null
    group by s.account_id, s.ad_id
    order by max_from_time desc
    limit 1000
    """

    return client.query_df(query)


@st.cache_data(ttl=CACHE_TTL)
def load_ch_dq_summary():
    query = """
    with ad_stats_src as (
        select *
        from schema.ad_stats final
        where from_time >= now() - interval 3 day
    ),
    ad_stats_duplicates as (
        select count() as cnt
        from (
            select account_id, ad_id, from_time
            from ad_stats_src
            group by account_id, ad_id, from_time
            having count() > 1
        )
    ),
    ad_stats_anomalies as (
        select count() as cnt
        from ad_stats_src
        where views < 0
           or opens < 0
           or clicks < 0
           or actions < 0
           or spent_budget < 0
           or clicks > views
           or opens > views
           or actions > views
           or from_time > to_time
    ),
    ads_list_duplicates as (
        select count() as cnt
        from (
            select account_id, ad_id
            from schema.ads_list final
            group by account_id, ad_id
            having count() > 1
        )
    ),
    orphan_stats as (
        select count() as cnt
        from (
            select s.account_id, s.ad_id
            from ad_stats_src s
            left join schema.ads_list a
                on s.account_id = a.account_id
               and s.ad_id = a.ad_id
            where a.ad_id is null
            group by s.account_id, s.ad_id
        )
    )
    select
        (select count() from ad_stats_src) as ad_stats_rows_3d,
        (select max(load_dttm) from ad_stats_src) as ad_stats_max_load_dttm,
        (select max(from_time) from ad_stats_src) as ad_stats_max_from_time,
        (select cnt from ad_stats_duplicates) as ad_stats_duplicate_keys,
        (select cnt from ad_stats_anomalies) as ad_stats_anomaly_rows,
        (select cnt from ads_list_duplicates) as ads_list_duplicate_keys,
        (select cnt from orphan_stats) as ad_stats_without_ads_list_keys
    """

    return client.query_df(query)


# =========================
# Рендер
# =========================
def render():
    st.title("Проверка данных в БД")

    st.session_state.setdefault("ch_df", None)
    st.session_state.setdefault("pg_vitrina_df", None)
    st.session_state.setdefault("pg_df", None)
    st.session_state.setdefault("dq_df", None)
    st.session_state.setdefault("dq_summary_df", None)

    col_cache_1, col_cache_2 = st.columns([1, 3])
    with col_cache_1:
        if st.button("Очистить кэш"):
            st.cache_data.clear()
            st.success("Кэш очищен")
    with col_cache_2:
        st.caption("Все запросы кэшируются на 10 минут")

    st.subheader("ClickHouse")

    if st.button("Загрузить данные CH"):
        with st.spinner("Запрос в ClickHouse..."):
            try:
                st.session_state["ch_df"] = load_clickhouse_data()
                st.success("Данные получены")
            except Exception as e:
                st.error(str(e))

    if st.session_state["ch_df"] is not None:
        st.dataframe(st.session_state["ch_df"], width="stretch")

    st.divider()

    st.subheader("Postgres")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ad_stats_vitrina")

        if st.button("Загрузить vitrina"):
            with st.spinner("Запрос в Postgres..."):
                try:
                    st.session_state["pg_vitrina_df"] = load_pg_vitrina()
                    st.success("Данные получены")
                except Exception as e:
                    st.error(str(e))

        if st.session_state["pg_vitrina_df"] is not None:
            st.dataframe(st.session_state["pg_vitrina_df"], width="stretch")

    with col2:
        st.markdown("### ad_stats")

        if st.button("Загрузить ad_stats"):
            with st.spinner("Запрос в Postgres..."):
                try:
                    st.session_state["pg_df"] = load_pg_ad_stats()
                    st.success("Данные получены")
                except Exception as e:
                    st.error(str(e))

        if st.session_state["pg_df"] is not None:
            st.dataframe(st.session_state["pg_df"], width="stretch")

    st.divider()
    st.subheader("Data Quality ClickHouse")

    try:
        summary_df = load_ch_dq_summary()
        st.session_state["dq_summary_df"] = summary_df

        if not summary_df.empty:
            row = summary_df.iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Строк ad_stats за 3 дня", int(row["ad_stats_rows_3d"]))
                st.metric("Дубли ad_stats", int(row["ad_stats_duplicate_keys"]))
            with c2:
                st.metric("Аномалии ad_stats", int(row["ad_stats_anomaly_rows"]))
                st.metric("Дубли ads_list", int(row["ads_list_duplicate_keys"]))
            with c3:
                st.metric("ad_stats без ads_list", int(row["ad_stats_without_ads_list_keys"]))
                st.metric("max from_time", str(row["ad_stats_max_from_time"]))
            with c4:
                st.metric("max load_dttm", str(row["ad_stats_max_load_dttm"]))
    except Exception as e:
        st.warning(f"Не удалось загрузить summary: {e}")

    dq_option = st.selectbox(
        "Выберите проверку",
        (
            "Свежесть ad_stats",
            "Дубли ad_stats",
            "Аномалии ad_stats",
            "Дубли ads_list",
            "ad_stats без ads_list",
        )
    )

    if st.button("Запустить проверку"):
        with st.spinner("Выполняем проверку..."):
            try:
                if dq_option == "Свежесть ad_stats":
                    st.session_state["dq_df"] = load_ch_ad_stats_freshness()

                elif dq_option == "Дубли ad_stats":
                    st.session_state["dq_df"] = load_ch_ad_stats_duplicates()

                elif dq_option == "Аномалии ad_stats":
                    st.session_state["dq_df"] = load_ch_ad_stats_anomalies()

                elif dq_option == "Дубли ads_list":
                    st.session_state["dq_df"] = load_ch_ads_list_duplicates()

                elif dq_option == "ad_stats без ads_list":
                    st.session_state["dq_df"] = load_ch_ad_stats_without_ads_list()

                st.success("Проверка выполнена")
            except Exception as e:
                st.error(str(e))

    if st.session_state["dq_df"] is not None:
        st.dataframe(st.session_state["dq_df"], width="stretch")