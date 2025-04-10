import streamlit as st
import stripe
from stripe.error import StripeError

# Set your Stripe secret key (store this securely, e.g., in environment variables)
stripe.api_key = st.secrets["stripe_api_key"]  # Replace with your actual secret key


def create_checkout_session(total_cost: float, data_selection: str):
    try:
        # Create a Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "paypal"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": data_selection,
                    },
                    "unit_amount": int(total_cost * 100),  # Stripe expects amount in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://pinnacledata.streamlit.app/?success=true",
            cancel_url="https://pinnacledata.streamlit.app/?cancel=true",
        )
        return session.url
    except StripeError as e:
        st.error(f"Error creating payment link: {str(e)}")
        return None


# Function to verify payment
def verify_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"
    except StripeError as e:
        st.error(f"Payment verification failed: {str(e)}")
        return False