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

    return conn.query(f"SELECT COUNT(id) FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_preview(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT * FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods} ORDER BY RAND() LIMIT 3")


def get_granular_event_ids(date_from: datetime, date_to: datetime, league_ids: str):

    return {event_id for event_id in conn.query(f"SELECT event_id FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids}")['event_id']}


def get_granular_rowcount(event_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT COUNT(id) FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_granular_fixtures_preview(date_from: datetime, date_to: datetime, league_ids: str):

    return conn.query(f"SELECT * FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} ORDER BY RAND() LIMIT 3")


def get_granular_odds_preview(event_ids: str, markets: str, periods: str):

    st.write(f"SELECT * FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods} ORDER BY id DESC LIMIT 3")
    return conn.query(f"SELECT * FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_granular_results_preview(event_ids: str, periods: str):

    return conn.query(f"SELECT * FROM {TABLE_RESULTS} WHERE event_id IN {event_ids} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_unique_leagues_id(sport: str, date_from: datetime, date_to: datetime, tour: str):

    if tour == 'All ATP Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ATP Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ATP Challenger Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ATP Challenger Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All WTA Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All WTA Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All WTA 125k Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All WTA 125k Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ITF Men Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ITF Men Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ITF Women Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ITF Women Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%' AND league_name LIKE '%Doubles%'")['league_id']}

