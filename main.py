import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st

import pandas as pd

      
def read_collection(collection_name):
    # Authenticate to Firestore with the JSON account key.
    db = firestore.Client.from_service_account_json("socmed-analytics-firebase-adminsdk-xqyvl-15c2e7c79d.json")

    # Create a reference to the Google post.
    collection_ref = db.collection(collection_name)
    
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
