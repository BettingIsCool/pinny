import streamlit as st
from config import TABLE_LEAGUES, TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_leagues(sport_id: int):
    """
    :param sport_id: The ID of the sport for which leagues are to be retrieved.
    :return: A list of tuples containing league IDs and league names for the given sport.
    """
    return conn.query(f"SELECT league_id, league_name FROM {TABLE_LEAGUES} WHERE sport_id = {sport_id}")
