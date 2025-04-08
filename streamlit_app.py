import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.title('PinnacleData by BettingIsCool')

import db_pinny as db
from datetime import datetime

from config import SPORTS

selected_sport = st.selectbox(label='Sport', options=SPORTS.keys(), help='You can request only one sport at a time. If you need data for more sports please submit multiple requests.')
selected_from_date = st.date_input(label='Start date', value=datetime.date(year=2021, month=1, day=1), min_value=datetime.date(year=2021, month=1, day=1), help='When should your data start? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')
selected_to_date = st.date_input(label='End date', value='today', min_value=datetime.date(year=2021, month=1, day=1), help='When should your data end? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')

#leagues = db.get_leagues(sport_id=19)
#st.sidebar(leagues)

