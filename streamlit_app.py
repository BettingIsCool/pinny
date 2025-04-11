import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.title('PinnacleData by BettingIsCool')

import datetime
import stripe_api
import pandas as pd
import db_pinny as db


from config import SPORTS, PERIODS, TABLE_CLOSING, TABLE_OPENING

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
    markets_count = len(selected_markets)
    selected_markets = [f"'{s}'" for s in selected_markets]
    selected_markets = f"({','.join(selected_markets)})"

    if selected_markets != '()':

        # Process periods
        period_options = {k[1]: v for k, v in PERIODS.items() if k[0] == SPORTS[selected_sport]}
        periods_count = len(period_options)
        selected_periods = st.multiselect(label='Periods', options=period_options.keys(), format_func=lambda x: period_options.get(x), help='Please select the periods you need the data for.')
        selected_periods = [f"{s}" for s in selected_periods]
        selected_periods = f"({','.join(selected_periods)})"

        if selected_periods != '()':

            if selected_type == 'Closing':

                # Get row count for selected data
                placeholder1 = st.empty()
                placeholder1.write(f":red[Looking up you data. This can take a while. Please be patient.]")
                rowcount = db.get_rowcount(table=TABLE_CLOSING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)[0]['COUNT(event_id)']
                placeholder1.empty()

                # Get total cost for selected data
                total_cost = rowcount / 2500
                data_selection = f'SUMMARY\n\n'
                data_selection += f'Your data selection has :green[{rowcount}] rows across :green[{leagues_count}] leagues.\n\n'
                data_selection += f'Total cost: :blue[€{total_cost:.2f}]\n'

                # Print summary
                st.write(data_selection)

                # Provide email
                email = st.text_input("Your email address (hit Enter when done)", max_chars=100, help='A download link will be sent to this email address.')

                if email != '':

                    # Create text for Stripe checkout
                    stripe_text = f'{selected_type} odds for {leagues_count} leagues and {markets_count} markets and {periods_count} periods from {selected_from_date} to {selected_to_date}. {rowcount} rows in csv format.'

                    # Generate and display Stripe payment link
                    if st.button("Proceed to Payment"):
                        session = stripe_api.create_checkout_session(total_cost=total_cost, stripe_text_for_client=stripe_text, selected_data=f'{email};Closing;{selected_sport};{selected_from_date};{selected_to_date};{selected_leagues};{selected_markets};{selected_periods}')
                        if session:
                            st.session_state["checkout_session_id"] = session.id
                            st.markdown(f"[Pay €{total_cost:.2f} Now]({session.url})")

                    # Show sneak preview
                    st.write('Here is a sneak preview of your data 👇')
                    st.write(pd.DataFrame(data=db.get_preview(table=TABLE_CLOSING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)))

            if selected_type == 'Opening':

                # Get row count for selected data
                placeholder1 = st.empty()
                placeholder1.write(f":red[Looking up you data. This can take a while. Please be patient.]")
                rowcount = db.get_rowcount(table=TABLE_OPENING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)[0]['COUNT(event_id)']
                placeholder1.empty()

                # Get total cost for selected data
                total_cost = rowcount / 2500
                data_selection = f'SUMMARY\n\n'
                data_selection += f'Your data selection has :green[{rowcount}] rows across :green[{leagues_count}] leagues.\n\n'
                data_selection += f'Total cost: :blue[€{total_cost:.2f}]\n'

                # Print summary
                st.write(data_selection)

                # Provide email
                email = st.text_input("Your email address (hit Enter when done)", max_chars=100, help='A download link will be sent to this email address.')

                if email != '':

                    # Create text for Stripe checkout
                    stripe_text = f'{selected_type} odds for {leagues_count} leagues and {markets_count} markets and {periods_count} periods from {selected_from_date} to {selected_to_date}. {rowcount} rows in csv format.'

                    # Generate and display Stripe payment link
                    if st.button("Proceed to Payment"):
                        session = stripe_api.create_checkout_session(total_cost=total_cost, stripe_text_for_client=stripe_text, selected_data=f'{email};Opening;{selected_sport};{selected_from_date};{selected_to_date};{selected_leagues};{selected_markets};{selected_periods}')
                        if session:
                            st.session_state["checkout_session_id"] = session.id
                            st.markdown(f"[Pay €{total_cost:.2f} Now]({session.url})")

                    # Show sneak preview
                    st.write('Here is a sneak preview of your data 👇')
                    st.write(pd.DataFrame(data=db.get_preview(table=TABLE_OPENING, date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)))

            if selected_type == 'Granular':

                # Get row count for selected data
                placeholder1 = st.empty()
                placeholder1.write(f":red[Looking up you data. This can take a while. Please be patient.]")
                event_ids = db.get_granular_event_ids(date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues)
                event_ids = [f"{s}" for s in event_ids]
                event_ids = f"({','.join(event_ids)})"
                rowcount = db.get_granular_rowcount(event_ids=event_ids, markets=selected_markets, periods=selected_periods)[0]['COUNT(id)']
                placeholder1.empty()

                # Get total cost for selected data
                total_cost = rowcount / 250000
                data_selection = f'SUMMARY\n\n'
                data_selection += f'Your data selection has :green[{rowcount}] rows across :green[{leagues_count}] leagues.\n\n'
                data_selection += f'Total cost: :blue[€{total_cost:.2f}]\n'

                # Print summary
                st.write(data_selection)
                st.write('You will receive 3 tables: :orange[fixtures], :orange[odds] and :orange[results]. Each event can be mapped via the unique :orange[event_id].')

                # Provide email
                email = st.text_input("Your email address (hit Enter when done)", max_chars=100,  help='A download link will be sent to this email address.')

                if email != '':

                    # Create text for Stripe checkout
                    stripe_text = f'{selected_type} odds for {leagues_count} leagues and {markets_count} markets and {periods_count} periods from {selected_from_date} to {selected_to_date}. {rowcount} rows in csv format.'

                    # Generate and display Stripe payment link
                    if st.button("Proceed to Payment"):
                        session = stripe_api.create_checkout_session(total_cost=total_cost, stripe_text_for_client=stripe_text, selected_data=f'{email};Granular;{selected_sport};{selected_from_date};{selected_to_date};{selected_leagues};{selected_markets};{selected_periods}')
                        if session:
                            st.session_state["checkout_session_id"] = session.id
                            st.markdown(f"[Pay €{total_cost:.2f} Now]({session.url})")

                    # Show sneak preview
                    st.write('Here is a sneak preview of your data 👇')
                    st.write('Fixtures')
                    st.write(pd.DataFrame(data=db.get_granular_fixtures_preview(date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues)))

                    st.write('Odds')
                    st.write(pd.DataFrame(data=db.get_granular_odds_preview(event_ids=event_ids, markets=selected_markets, periods=selected_periods)))

                    st.write('Results')
                    st.write(pd.DataFrame(data=db.get_granular_results_preview(event_ids=event_ids, periods=selected_periods)))


# Check for redirect (success or cancel) and display message
query_params = st.query_params  # Using the updated method
if "success" in query_params or "cancel" in query_params:
    st.success("Order submitted. We are processing your request. You will receive a download link via email once the data is ready.")
