import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st

import json
import pandas as pd

      
def read_collection(collection_name):
    # Authenticate to Firestore with the JSON account key.
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

st.header('Tiktok stats for tiktok.com/mvrco_poloo')

data = read_collection("tiktok_scraper")
df = pd.DataFrame(data).sort_values("finished_at").head(20)
st.line_chart(data=df, x="finished_at", y="engagement_score")
