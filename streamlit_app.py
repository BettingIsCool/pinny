import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.markdown('PinnacleData by BettingIsCool')

import db_pinny as db

leagues = db.get_leagues(sport_id=19)
st.write(leagues)

