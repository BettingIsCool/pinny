import datetime
import streamlit as st
from config import TABLE_LEAGUES, TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS, TABLE_OPENING, TABLE_CLOSING

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_unique_leagues(sport: str, date_from: datetime, date_to: datetime):

    return conn.query(f"SELECT DISTINCT(league_id), league_name FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}'")


def get_closing_event_ids(date_from: datetime, date_to: datetime, league_ids: list, markets: list, periods: list):

    st.write(f"SELECT COUNT(event_id) FROM {TABLE_CLOSING} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}")
    return conn.query(f"SELECT COUNT(event_id) FROM {TABLE_CLOSING} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


