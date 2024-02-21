import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st
import altair as alt
import re

import json
import pandas as pd

class AppUtils:
    def __init__(self):
        service_account_json = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["client_x509_cert_url"],
            "universe_domain": "googleapis.com"
        }

        cred = credentials.Certificate(service_account_json)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
    def upload_record(self, collection_name, data):
        client = firestore.client()
        doc_ref = client.collection(collection_name).document()
        doc_ref.set(data)


    def read_collection(self, collection_name):
        # Authenticate to Firestore with the JSON account key.
        
        client = firestore.client()
        collection_ref = client.collection(collection_name)
        

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
        
        # Return True if the email matches the pattern, False otherwise
        return bool(match)

appUtils = AppUtils()

# Popup email list
with st.form("my_form"):
    st.write("Email signup")
    email = st.text_input("Enter email here")
    submitted = st.form_submit_button("Submit")
    if submitted and appUtils.is_valid_email(email):
        st.write("email", email)
        appUtils.upload_record("email_list", {"email": email, "source": "socmed_analytics_app"})



# Chart
st.header('Stats for tiktok.com/mvrco_poloo')
st.write("Engagement score")
data = appUtils.read_collection("tiktok_scraper")
df = pd.DataFrame(data).sort_values("finished_at").head(20)
c = (
   alt.Chart(df)
   .mark_line()
   .encode(alt.Y('engagement_score').scale(zero=False), x="finished_at")
)
st.altair_chart(c, use_container_width=True)

# Latest stats
st.write("This week:")
latest_row = df.tail(1).iloc[0]

if latest_row["total_diggCount_diff"] != 0:
    sign = "+" if latest_row["total_diggCount_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['total_diggCount_diff']} likes")

if latest_row["total_shareCount_diff"] != 0:
    sign = "+" if latest_row["total_shareCount_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['total_shareCount_diff']} shares")

if latest_row["total_collectCount_diff"] != 0:
    sign = "+" if latest_row["total_collectCount_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['total_collectCount_diff']} saves")

if latest_row["total_commentCount_diff"] != 0:
    sign = "+" if latest_row["total_commentCount_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['total_commentCount_diff']} comments")

if latest_row["total_playCount_diff"] != 0:
    sign = "+" if latest_row["total_playCount_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['total_playCount_diff']} plays")

if latest_row["follower_count_diff"] != 0:
    sign = "+" if latest_row["follower_count_diff"] > 0 else "-"
    st.write(f"{sign}{latest_row['follower_count_diff']} followers")

