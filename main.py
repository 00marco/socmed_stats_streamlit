import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st


def read_collection(collection_name):
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("socmed-analytics-firebase-adminsdk-xqyvl-15c2e7c79d.json")
    app = firebase_admin.initialize_app(cred)

    # Initialize Firestore client
    db = firestore.client()
    # Get a Firestore reference to the specified collection
    collection_ref = db.collection(collection_name)
    
    # Retrieve documents from the collection
    docs = collection_ref.stream()
    
    # Iterate over the documents and print them
    for doc in docs:
        print(f"Document ID: {doc.id}")
        print(f"Data: {doc.to_dict()}")


st.header('Hello 🌎!')
if st.button('Balloons?'):
    st.balloons()
