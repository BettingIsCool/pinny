import ast
import datetime
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


def get_granular_rowcount_parameterized(event_ids: str, markets: str, periods: str):
    # Parse string inputs into lists
    try:
        event_ids_list = ast.literal_eval(event_ids) if event_ids else []
        markets_list = ast.literal_eval(markets) if markets else []
        periods_list = ast.literal_eval(periods) if periods else []
    except (ValueError, SyntaxError):
        event_ids_list = [int(x) for x in event_ids.split(',') if x.strip()] if event_ids else []
        markets_list = [x.strip() for x in markets.split(',') if x.strip()] if markets else []
        periods_list = [int(x) for x in periods.split(',') if x.strip()] if periods else []

    # Create placeholders for IN clauses
    event_placeholders = ','.join([f':event_id_{i}' for i in range(len(event_ids_list))])
    market_placeholders = ','.join([f':market_{i}' for i in range(len(markets_list))])
    period_placeholders = ','.join([f':period_{i}' for i in range(len(periods_list))])

    # Handle empty lists (to avoid invalid SQL)
    if not event_ids_list:
        event_placeholders = 'NULL'
    if not markets_list:
        market_placeholders = 'NULL'
    if not periods_list:
        period_placeholders = 'NULL'

    # Parameterized query
    query = text(
        f"SELECT COUNT(id) FROM {TABLE_ODDS} "
        f"WHERE event_id IN ({event_placeholders}) "
        f"AND market IN ({market_placeholders}) "
        f"AND period IN ({period_placeholders})"
    )

    # Prepare parameters
    params = {}
    for i, eid in enumerate(event_ids_list):
        params[f'event_id_{i}'] = eid
    for i, m in enumerate(markets_list):
        params[f'market_{i}'] = m
    for i, p in enumerate(periods_list):
        params[f'period_{i}'] = p

    # Execute query
    result = conn.execute(query, params)

    # Convert to dict format
    return result.mappings().all()  # Equivalent to pandas to_dict('records')

