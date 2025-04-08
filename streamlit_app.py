import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.markdown('## **PinnacleData by BettingIsCool. Structured betting data.**')

import db_pinny as db
from config import SPORTS

selected_sport = st.selectbox(label='Sport', options=SPORTS.keys(), help='Select sport')

#leagues = db.get_leagues(sport_id=19)
#st.sidebar(leagues)

