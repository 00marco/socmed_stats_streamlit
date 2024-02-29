import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st
import altair as alt
import re
from validate_email import validate_email
from st_paywall import add_auth


import json
import pandas as pd

import hashlib
import uuid 
from datetime import datetime, timedelta


class AppUtils:
    def __init__(self):
        service_account_json = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email_firebase"],
            "client_id": st.secrets["client_id_firebase"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["client_x509_cert_url"],
            "universe_domain": "googleapis.com"
        }

        cred = credentials.Certificate(service_account_json)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

    def hash_string(self, input_string):
        # Convert the input string to bytes
        input_bytes = input_string.encode('utf-8')
        
        # Create a SHA-256 hash object
        sha256_hash = hashlib.sha256()
        
        # Update the hash object with the input bytes
        sha256_hash.update(input_bytes)
        
        # Get the hexadecimal representation of the hash
        hashed_string = sha256_hash.hexdigest()
        
        return hashed_string

    def upload_record_if_not_exists(self, collection_name, data):
        # Check if the record already exists
        doc_ref = self.client.collection(collection_name).document(self.hash_string(data["email"])).set(data)

    def read_collection(self, collection_name):
        # Authenticate to Firestore with the JSON account key.
        
        self.client = firestore.client()
        collection_ref = self.client.collection(collection_name)
        
        # Retrieve documents from the collection
        docs = collection_ref.stream()
        
        # Iterate over the documents and print them
        data = []
        for doc in docs:
            print(f"Document ID: {doc.id}")
            print(f"Data: {doc.to_dict()['dataset_id']}, {doc.to_dict()['finished_at']}, {doc.to_dict()['engagement_score_diff']}")
            data.append(doc.to_dict())

        return data

    def is_valid_email(self, email):
        """
        Check if the provided string is a valid email address.
        """
        # Regular expression pattern for validating email addresses
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Match the pattern with the email string
        match = re.match(email_pattern, email)
        
        # is_valid = validate_email(email_address=email) # idk its annoying
        is_valid = True

        # Return True if the email matches the pattern, False otherwise
        return bool(match) and is_valid

    def on_click(self, appUtils):
        if appUtils.is_valid_email(st.session_state.email):
            st.toast("Thank you for your interest! \nWe'll keep you updated on our progress.", icon="🚀")
            appUtils.upload_record_if_not_exists("email_list", {"email": st.session_state.email, 
                                                                "source": "socmed_analytics_app",
                                                                "question_1": "Any suggestions?",
                                                                "answer_1": st.session_state.answer_interest,
                                                                "question_2": "How much would you pay for a service like this?",
                                                                "answer_2": st.session_state.answer_price,
                                                                "date_submitted": datetime.now()}
            )
            st.session_state.email = ""
            st.session_state.answer_interest = None
            st.session_state.answer_price = 0
            st.session_state.submitted = False
        else:
            st.toast("Please enter a valid email address.", icon="🚫")
            # st.session_state.email = ""
            # st.session_state.answer_interest = None
            # st.session_state.answer_price = 0
            # st.session_state.submitted = False

    def next_sunday(self, ):
        today = datetime.now()
        days_until_sunday = (6 - today.weekday()) % 7  # Calculate days until next Sunday
        next_sunday_date = today + timedelta(days=days_until_sunday)
        return next_sunday_date.strftime("%A, %B %d, %Y")

appUtils = AppUtils()


# Sidebar
with st.sidebar:
    st.title("LazyMetrics 📊")
    st.write("Get the gist with one look!")
    st.write("")

add_auth(required=False, login_sidebar=True, subscribe_now_sidebar=False)

with st.sidebar:
    st.divider()
    st.subheader("🧍Target Audience:")
    st.markdown("Need to grow a Tiktok account but hate scrolling? This might be for you *(Instagram metrics coming soon!)*")

    next_run = appUtils.next_sunday()
    st.subheader(f"⏰ Next run on: {next_run}")
    st.write("Stop obsessing. Your next reel isn't going to edit itself")

    st.divider()

    with st.form("my_form"):
        st.write("Still validating this idea, let me know what you think! 🧪📊")
        answer_interest = st.text_input("Any suggestions?", key="answer_interest")
        answer_price = st.number_input("How much would you pay for a service like this? (USD)", min_value=0, key="answer_price")
        email = st.text_input("Would you like to receive launch updates via email? Enter your email address below!", key="email")
        submitted = st.form_submit_button("Submit", on_click=appUtils.on_click, args=[appUtils])

# Chart
if len(st.session_state.get("email", "")) > 0 and not st.session_state.get("user_subscribed", False):
    st.write("")
    st.divider()

if st.session_state.get("user_subscribed", False) is False:
    st.header('Demo:')
else:
    st.header("Welcome!")
    # instagram_user = st.write("Instagram Account Name: ")
    # tiktok_user = st.write("Tiktok Account Name: ")
    # st.button("Get data")

data = appUtils.read_collection("tiktok_scraper")
df = pd.DataFrame(data).sort_values("finished_at").head(20)
df["finished_at"] = pd.to_datetime(df["finished_at"]).dt.date
c = (
alt.Chart(df, title="Engagement score for tiktok.com/mvrco_poloo's account over time:")
.mark_line()
.encode(alt.Y('engagement_score').scale(zero=False).title("Engagement Score"), x=alt.Y('finished_at').scale(zero=False).title("Date"))
.properties(height=600)
)
st.altair_chart(c, use_container_width=True)
latest_row = df.tail(1).iloc[0]

if latest_row["engagement_score_diff"] > 0:
    st.success("You're doing great this week. Keep it up! 🎉🎉")
else:
    st.error("You're not doing so well this week. Try to post more engaging content! ✊✊")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")