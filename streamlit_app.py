import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.title('PinnacleData by BettingIsCool')

import datetime
import db_pinny as db


from config import SPORTS, PERIODS

selected_type = st.selectbox(label='Type', options=['Opening', 'Closing', 'Granular'], help='What type of data do you need? Opening...opening odds, Closing...closing odds, Granular...all odds (the complete odds history for each match updated roughly every 10 seconds).')
selected_sport = st.selectbox(label='Sport', options=SPORTS.keys(), help='You can request only one sport at a time. If you need data for more sports please submit multiple requests.')
selected_from_date = st.date_input(label='Start date', value=datetime.date(year=2021, month=1, day=1), min_value=datetime.date(year=2021, month=1, day=1), help='When should your data start? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')
selected_to_date = st.date_input(label='End date', value='today', min_value=datetime.date(year=2021, month=1, day=1), help='When should your data end? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')

# Get leagues
leagues_df = db.get_unique_leagues(sport=selected_sport, date_from=selected_from_date, date_to=selected_to_date)
leagues = dict(zip(leagues_df.league_id, leagues_df.league_name))
selected_leagues = st.multiselect(label='Leagues', options=sorted(leagues.keys()), format_func=lambda x: leagues.get(x), placeholder='Start typing...', help='Please select the leagues you need the data for.')

selected_markets = st.multiselect(label='Markets', options=['moneyline', 'spread', 'totals', 'home_totals', 'away_totals'], help='Please select the markets you need the data for.')

period_options = dict()
for k, v in PERIODS.items():
    if k[0] == SPORTS[selected_sport]:
        period_options.update({k[1]: v})

st.write(period_options)

selected_periods = st.multiselect(label='Periods', options=period_options.keys(), format_func=lambda x: period_options.get(x), help='Please select the periods you need the data for.')

# Get markets


st.write(selected_leagues)
st.write(selected_markets)
st.write(selected_periods)

#selected_leagues = st.selectbox("Leagues", options=sorted(leagues))

#st.write(leagues)

