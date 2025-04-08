import datetime
import streamlit as st
from config import TABLE_LEAGUES, TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_unique_leagues(sport: str, date_from: datetime, date_to: datetime):
    """
    :param username: The username of the user whose unique leagues are to be fetched.
    :param sports: A string representing the sports categories to filter the leagues.
    :return: A list of unique league names associated with the user and filtered by the specified sports.
    """
    return conn.query(f"SELECT DISTINCT(league_name), league_id FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}'").to_dict()
