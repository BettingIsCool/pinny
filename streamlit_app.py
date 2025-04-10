import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.title('PinnacleData by BettingIsCool')

import datetime
import stripe_api
import pandas as pd
import db_pinny as db



from config import SPORTS, PERIODS, TABLE_CLOSING

selected_type = st.selectbox(label='Type', options=['Opening', 'Closing', 'Granular'], help='What type of data do you need? Opening...opening odds, Closing...closing odds, Granular...all odds (the complete odds history for each match updated roughly every 10 seconds).')
selected_sport = st.selectbox(label='Sport', options=SPORTS.keys(), help='You can request only one sport at a time. If you need data for more sports please submit multiple requests.')
selected_from_date = st.date_input(label='Start date', value=datetime.date(year=2021, month=1, day=1), min_value=datetime.date(year=2021, month=1, day=1), help='When should your data start? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')
selected_to_date = st.date_input(label='End date', value='today', min_value=datetime.date(year=2021, month=1, day=1), help='When should your data end? You can either use the calendar or manually enter the date, i.e. 2024/08/19.')

# Get leagues
leagues_df = db.get_unique_leagues(sport=selected_sport, date_from=selected_from_date, date_to=selected_to_date)
leagues = dict(zip(leagues_df.league_id, leagues_df.league_name))
selected_leagues = st.multiselect(label='Leagues', options=sorted(leagues.keys()), format_func=lambda x: leagues.get(x), placeholder='Start typing...', help='Please select the leagues you need the data for.')
leagues_count = len(selected_leagues)
selected_leagues = [f"{s}" for s in selected_leagues]
selected_leagues = f"({','.join(selected_leagues)})"

if selected_leagues != '()':

    # Process markets
    selected_markets = st.multiselect(label='Markets', options=['moneyline', 'spread', 'totals', 'home_totals', 'away_totals'], help='Please select the markets you need the data for.')
    selected_markets = [f"'{s}'" for s in selected_markets]
    selected_markets = f"({','.join(selected_markets)})"

    if selected_markets != '()':

        # Process periods
        period_options = {k[1]: v for k, v in PERIODS.items() if k[0] == SPORTS[selected_sport]}
        selected_periods = st.multiselect(label='Periods', options=period_options.keys(), format_func=lambda x: period_options.get(x), help='Please select the periods you need the data for.')
        selected_periods = [f"{s}" for s in selected_periods]
        selected_periods = f"({','.join(selected_periods)})"

        if selected_periods != '()':

            if selected_type == 'Closing':

                rowcount = db.get_rowcount(table=TABLE_CLOSING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)[0]['COUNT(event_id)']

                total_cost = rowcount / 2500
                data_selection = f'SUMMARY\n'
                data_selection += f'Your data selection has {rowcount} rows across {leagues_count} leagues.\n\n'
                data_selection += f'Total cost: €{total_cost:.2f}\n'

                stripe_text = f'Betting Data for {leagues_count} leagues, {rowcount} rows.'

                st.write(data_selection)
                preview = db.get_preview(table=TABLE_CLOSING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)
                preview_df = pd.DataFrame(data=preview)
                st.write(preview_df)

                # Step 3: Generate and display Stripe payment link
                if st.button("Proceed to Payment"):
                    payment_url = stripe_api.create_checkout_session(total_cost=total_cost, data_selection=stripe_text)
                    if payment_url:
                        st.write("Click the link below to complete your payment:")
                        st.markdown(f"[Pay €{total_cost:.2f} Now]({payment_url})")
