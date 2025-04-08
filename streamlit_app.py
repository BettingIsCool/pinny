import streamlit as st
import db_pinnacle_remote as db

leagues = db.get_leagues(sport_id=19)
st.write(leagues)