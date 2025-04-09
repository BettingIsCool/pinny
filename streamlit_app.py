import streamlit as st

st.set_page_config(page_title="PinnacleData by BettingIsCool", page_icon="💾", layout="wide", initial_sidebar_state="expanded")
st.title('PinnacleData by BettingIsCool')

import datetime
import stripe_api
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
selected_leagues = [f"{s}" for s in selected_leagues]
selected_leagues = f"({','.join(selected_leagues)})"

# Process markets
selected_markets = st.multiselect(label='Markets', options=['moneyline', 'spread', 'totals', 'home_totals', 'away_totals'], help='Please select the markets you need the data for.')
selected_markets = [f"'{s}'" for s in selected_markets]
selected_markets = f"({','.join(selected_markets)})"

# Process periods
period_options = {k[1]: v for k, v in PERIODS.items() if k[0] == SPORTS[selected_sport]}
selected_periods = st.multiselect(label='Periods', options=period_options.keys(), format_func=lambda x: period_options.get(x), help='Please select the periods you need the data for.')
selected_periods = [f"{s}" for s in selected_periods]
selected_periods = f"({','.join(selected_periods)})"

if selected_type == 'Closing':

    rowcount = db.get_closing_event_ids(date_from=selected_from_date, date_to=selected_to_date, league_ids=selected_leagues, markets=selected_markets, periods=selected_periods)

    total_cost = rowcount[0]['COUNT(event_id)'] / 2500
    data_selection = 'Your data selection.'

    st.write(rowcount)
    st.write(f"Cost: €{total_cost:.2f}")

    st.title("Pinnacle Betting Data Download")

    # Step 3: Generate and display Stripe payment link
    if st.button("Proceed to Payment"):
        payment_url = stripe_api.create_checkout_session(total_cost=total_cost, data_selection=data_selection)
        if payment_url:
            st.write("Click the link below to complete your payment:")
            st.markdown(f"[Pay ${total_cost:.2f} Now]({payment_url})")

    # Check URL parameters for success
    query_params = st.experimental_get_query_params()
    if "success" in query_params and query_params["success"][0] == "true":
        # Normally, you'd pass the session_id via URL or session state
        # For simplicity, assume it's stored in session state (see below)
        if "checkout_session_id" in st.session_state:
            session_id = st.session_state["checkout_session_id"]
            if stripe_api.verify_payment(session_id):
                st.success("Payment successful! Preparing your data...")
                # Proceed to Step 5
            else:
                st.error("Payment not verified. Please contact support.")
        else:
            st.error("Session ID not found.")
    else:
        # Continue from Step 3 code
        if st.button("Proceed to Payment"):
            payment_url = stripe_api.create_checkout_session(total_cost, data_selection)
            if payment_url:
                # Store session ID in session state for verification
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": f"Betting Data - {data_selection}",
                            },
                            "unit_amount": int(total_cost * 100),
                        },
                        "quantity": 1,
                    }],
                    mode="payment",
                    success_url="https://pinnacledata.streamlit.app/?success=true",
                    cancel_url="https://pinnacledata.streamlit.app/?cancel=true",
                )
                st.session_state["checkout_session_id"] = session.id
                st.markdown(f"[Pay ${total_cost:.2f} Now]({payment_url})")



