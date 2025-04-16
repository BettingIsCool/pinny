import datetime
import pandas as pd
import streamlit as st
from sqlalchemy.sql import text
from config import TABLE_LEAGUES, TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS, TABLE_OPENING, TABLE_CLOSING

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_unique_leagues(sport: str, date_from: datetime, date_to: datetime):

    return conn.query(f"SELECT DISTINCT(league_id), league_name FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}'")


def get_rowcount(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT COUNT(event_id) FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_preview(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT * FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods} ORDER BY RAND() LIMIT 3")


def get_granular_event_ids(date_from: datetime, date_to: datetime, league_ids: str):

    return {event_id for event_id in conn.query(f"SELECT event_id FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids}")['event_id']}


def get_granular_rowcount(event_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT COUNT(id) FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')

def get_granular_fixtures_preview(date_from: datetime, date_to: datetime, league_ids: str):

    return conn.query(f"SELECT * FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} ORDER BY RAND() LIMIT 3")


def get_granular_odds_preview(event_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT * FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_granular_results_preview(event_ids: str, periods: str):

    return conn.query(f"SELECT * FROM {TABLE_RESULTS} WHERE event_id IN {event_ids} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_unique_leagues_id(sport: str, date_from: datetime, date_to: datetime, tour: str):

    if tour == 'ATP':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%'")['league_id']}
    elif tour == 'ATP Challenger':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%'")['league_id']}
    elif tour == 'WTA':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%'")['league_id']}
    elif tour == 'WTA 125k':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%'")['league_id']}
    elif tour == 'ITF Men':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%'")['league_id']}
    elif tour == 'ITF Women':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%'")['league_id']}


def get_granular_rowcount_temp_tables(event_ids: str, markets: str, periods: str):
    # Parse input strings without ast (e.g., "1,2,3", "(1,2,3)", "[1,2,3]")
    def parse_input(input_str: str, is_int: bool = False) -> list:
        if not input_str:
            return []
        # Remove parentheses, brackets, and whitespace
        cleaned = input_str.strip().strip('()[]').replace(' ', '')
        # Split on commas and filter out empty values
        values = [v.strip() for v in cleaned.split(',') if v.strip()]
        # Convert to int if specified (for event_id, period)
        return [int(v) if is_int else v for v in values]

    # Parse inputs
    event_ids_list = parse_input(event_ids, is_int=True)  # event_id as INT
    markets_list = parse_input(markets, is_int=False)     # market as VARCHAR
    periods_list = parse_input(periods, is_int=True)      # period as INT

    # Hardcode table name to prevent injection
    TABLE_ODDS = 'odds'  # Replace with your actual table name

    # Handle small IN clauses with parameterized query
    if len(event_ids_list) <= 50 and len(markets_list) <= 50 and len(periods_list) <= 50:
        # Create placeholders for IN clauses
        event_placeholders = ','.join([f':e{i}' for i in range(len(event_ids_list))])
        market_placeholders = ','.join([f':m{i}' for i in range(len(markets_list))])
        period_placeholders = ','.join([f':p{i}' for i in range(len(periods_list))])

        # Handle empty lists
        if not event_ids_list:
            event_placeholders = 'NULL'
        if not markets_list:
            market_placeholders = 'NULL'
        if not periods_list:
            period_placeholders = 'NULL'

        # Parameterized query
        query = text(
            f"SELECT COUNT(id) AS count FROM {TABLE_ODDS} "
            f"WHERE event_id IN ({event_placeholders}) "
            f"AND market IN ({market_placeholders}) "
            f"AND period IN ({period_placeholders})"
        )

        # Prepare parameters
        params = {}
        for i, eid in enumerate(event_ids_list):
            params[f'e{i}'] = eid
        for i, m in enumerate(markets_list):
            params[f'm{i}'] = m
        for i, p in enumerate(periods_list):
            params[f'p{i}'] = p

        # Execute with pandas (assuming conn.query is pandas.read_sql)
        df = pd.read_sql(query, conn, params=params)
        return df.to_dict('records')

    # Handle large IN clauses with temporary tables
    else:
        # Create temporary tables
        conn.execute(text("CREATE TEMPORARY TABLE temp_event_ids (event_id INT)"))
        if event_ids_list:
            conn.execute(
                text("INSERT INTO temp_event_ids (event_id) VALUES (:eid)"),
                [{'eid': eid} for eid in event_ids_list]
            )
        conn.execute(text("CREATE TEMPORARY TABLE temp_markets (market VARCHAR(255))"))
        if markets_list:
            conn.execute(
                text("INSERT INTO temp_markets (market) VALUES (:m)"),
                [{'m': m} for m in markets_list]
            )
        conn.execute(text("CREATE TEMPORARY TABLE temp_periods (period INT)"))
        if periods_list:
            conn.execute(
                text("INSERT INTO temp_periods (period) VALUES (:p)"),
                [{'p': p} for p in periods_list]
            )

        # Add indexes to temporary tables for performance
        conn.execute(text("CREATE INDEX idx_temp_event_id ON temp_event_ids (event_id)"))
        conn.execute(text("CREATE INDEX idx_temp_market ON temp_markets (market)"))
        conn.execute(text("CREATE INDEX idx_temp_period ON temp_periods (period)"))

        # Query with joins
        query = text(
            f"SELECT COUNT(o.id) AS count FROM {TABLE_ODDS} o "
            "JOIN temp_event_ids e ON o.event_id = e.event_id "
            "JOIN temp_markets m ON o.market = m.market "
            "JOIN temp_periods p ON o.period = p.period"
        )

        # Execute with pandas
        df = pd.read_sql(query, conn)
        return df.to_dict('records')
