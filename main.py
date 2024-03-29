import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st
import altair as alt
import re
from validate_email import validate_email
from st_paywall import add_auth
from streamlit_extras.grid import grid

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

        self.client = firestore.client()

    def hash_string(self, input_string):
        print("input string", input_string)
        # Convert the input string to bytes
        input_bytes = input_string.encode('utf-8')
        
        # Create a SHA-256 hash object
        sha256_hash = hashlib.sha256()
        
        # Update the hash object with the input bytes
        sha256_hash.update(input_bytes)
        
        # Get the hexadecimal representation of the hash
        hashed_string = sha256_hash.hexdigest()
        
        print("hashed string", hashed_string)

        return hashed_string

    def check_user_if_exists(self, email):
        try:
            doc_ref = self.client.collection("user").document(self.hash_string(email)).get()
            return doc_ref.to_dict()
        except Exception as e:
            return None
    
    def upload_record_if_not_exists(self, collection_name, data):
        # Check if the record already exists
        doc_ref = self.client.collection(collection_name).document(self.hash_string(data["email"])).set(data)
        print(f"{data} uploaded")

    def read_collection(self, collection_name):
        # Authenticate to Firestore with the JSON account key.
        
        collection_ref = self.client.collection(collection_name)
        
        # Retrieve documents from the collection
        docs = collection_ref.stream()
        
        # Iterate over the documents and print them
        data = []
        for doc in docs:
            # print(f"Document ID: {doc.id}")
            # print(f"Data: {doc.to_dict()['dataset_id']}, {doc.to_dict()['finished_at']}, {doc.to_dict()['engagement_score_diff']}")
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

    def toggle_demo_user(self):
        if st.session_state.demo_user_selectbox == "Demo User 1 (mvrco_poloo)":
            st.session_state.tiktok_handle = "mvrco_poloo"
            st.session_state.instagram_handle = "mvrco_poloo"
        elif st.session_state.demo_user_selectbox == "Demo User 2 (le_sserafim)":
            st.session_state.tiktok_handle = "LE SSERAFIM"
            st.session_state.instagram_handle = "le_sserafim"
        else:  
            st.session_state.tiktok_handle = "enhypen"
            st.session_state.instagram_handle = "enhypen"
            
        # st.toast("toggle")
        # st.toast(st.session_state.tiktok_handle)
        # st.toast(st.session_state.instagram_handle)
        
    def get_chart(self):
        # st.toast("get chart")
        # st.toast(st.session_state.tiktok_handle)
        # st.toast(st.session_state.instagram_handle)

        data = appUtils.read_collection("metrics")
        df = pd.DataFrame(data)
        df = df.loc[(df["account_name"]==st.session_state.tiktok_handle) |( df["account_name"]==st.session_state.instagram_handle)]
        df = df.sort_values("timestamp")
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date

        scale = alt.Scale(
            domain=["tiktok", "instagram"],
            range=["#2af0ea", "#E1306C"],
        )
        color = alt.Color("source:N", scale=scale)
        c = (
            alt.Chart(df)
            .mark_line()
            .encode(alt.Y('engagement_score').scale(zero=False).title("Engagement Score"), 
                    x=alt.Y('timestamp').scale(zero=False).title("Date"),
                    color=color)
            .properties(height=600)
        )
        # st.toast(f"df shape: {df.shape}")
        return c, df



appUtils = AppUtils()

def login_callback():
    pass


# Initialization
if "instagram_handle" not in st.session_state or "tiktok_handle" not in st.session_state:
    st.session_state.tiktok_handle = "mvrco_poloo"
    st.session_state.instagram_handle = "mvrco_poloo"
st.set_page_config(layout="wide")



# Sidebar
with st.sidebar:
    st.title("LazyMetrics 📊")
    st.write("Social media metrics minus the doomscrolling. 🚀")
    # if not st.session_state.get("email", False):
    #     st.write("")
    #     st.write("")
    #     st.write("*(Logging in will create a new tab -- bad UX I know, but it's an annoying bug. 💀)*")
    #     st.write("")

# Authentication
add_auth(required=False, 
         login_sidebar=True, 
         subscribe_now_sidebar=True, 
         on_login=login_callback)

    

# Welcome text
st.title("Hello!")
st.divider()
    
# Select demo user if not logged in
if not st.session_state.get("user_subscribed", False):
    st.selectbox(
        "Select demo user",
        ("Demo User 1 (mvrco_poloo)", "Demo User 2 (le_sserafim)", "Demo User 3 (enhypen)"), 
        key="demo_user_selectbox",
        on_change=appUtils.toggle_demo_user,
    )
    st.divider()


# Create user if it doesn't exist yet.
# If it does, get user data
# If not yet logged in, show demo page
if st.session_state.get("email", None):
    user = appUtils.check_user_if_exists(st.session_state.email)
    warn_before_delete = False
    if user is not None:
        st.toast(f"user exists: {user}")
        tiktok_handle_from_db = user.get("data", {}).get("tiktok_handle")
        instagram_handle_from_db = user.get("data", {}).get("instagram_handle")
        if not tiktok_handle_from_db or not instagram_handle_from_db:
            warn_before_delete = True
    else:
        user = {}
        st.toast("no record found")
        appUtils.upload_record_if_not_exists("user",
                                             data={
                                                 "email": st.session_state.email,
                                                 "data": {}
                                             })
        tiktok_handle_from_db = ""
        instagram_handle_from_db = ""
    
    # If user is subscribed, then show controls
    if st.session_state.get("user_subscribed", False):
        user_input_grid = grid([5,1], [5,1], [5,1], [5,1], vertical_align="bottom")
        user_input_grid.text_input("Tiktok handle", placeholder=tiktok_handle_from_db, key="tiktok_handle_user_input")
        if user_input_grid.button("Update", key="save_tiktok_handle"):
            user_input_grid.text_input("Confirm delete", placeholder="Write your email to confirm deletion", key="email_to_confirm_delete_tiktok_handle")
            if user_input_grid.button("Delete", type="primary"):
                if st.session_state.email_to_confirm_delete_tiktok_handle == st.session_state.email:
                    # appUtils.upload_record_if_not_exists("user",
                    #                                     data={
                    #                                         "email": st.session_state.email,
                    #                                         "data": {}
                    #                                     })
                    # appUtils.delete_user_data(st.session_state.email)

                    # st.session_state.email_to_confirm_delete = ""
                    # st.session_state.tiktok_handle = ""
                    # st.session_state.instagram_handle = ""
                    # st.session_state.tiktok_handle_user_input = ""
                    # st.session_state.instagram_handle_user_input = ""

                    # appUtils.upload_record_if_not_exists("user",
                    #     data={
                    #         "email": st.session_state.email,
                    #         "data": {
                    #             "instagram_handle": st.session_state.instagram_handle_from_db,
                    #             "tiktok_handle": st.session_state.tiktok_handle_user_input
                    #         }
                    #     })
                    st.toast("Deleted user data.")
                else:
                    st.toast("Incorrect email")
        user_input_grid.write("")
        user_input_grid.write("")
                
        user_input_grid.text_input("Instagram handle", placeholder=instagram_handle_from_db, key="instagram_handle_user_input")
        if user_input_grid.button("Update", key="save_instagram_handle"):
            user_input_grid.text_input("Confirm delete", placeholder="Write your email to confirm deletion", key="email_to_confirm_delete_instagram_handle")
            if user_input_grid.button("Delete", type="primary"):
                if st.session_state.email_to_confirm_delete == st.session_state.email:
                    # appUtils.upload_record_if_not_exists("user",
                    #                                     data={
                    #                                         "email": st.session_state.email,
                    #                                         "data": {}
                    #                                     })
                    # appUtils.delete_user_data(st.session_state.email)

                    # st.session_state.email_to_confirm_delete = ""
                    # st.session_state.tiktok_handle = ""
                    # st.session_state.instagram_handle = ""
                    # st.session_state.tiktok_handle_user_input = ""
                    # st.session_state.instagram_handle_user_input = ""

                    # appUtils.upload_record_if_not_exists("user",
                    #     data={
                    #         "email": st.session_state.email,
                    #         "data": {
                    #             "instagram_handle": st.session_state.instagram_handle_from_db,
                    #             "tiktok_handle": st.session_state.tiktok_handle_user_input
                    #         }
                    #     })
                    st.toast("Deleted user data.")
                else:
                    st.toast("Incorrect email")
            else: 
                user_input_grid.write("")
        else:
            user_input_grid.write("")
        
        
        # This section allows user to reset instagram and tiktok handles
        st.divider()
    else:
        st.write("")
        
    st.balloons()


# Chart
if st.session_state.get("email", None):
    st.header("Engagement Score")
else:
    st.header("(Demo) Engagement Score")
st.write("Likes, comments, shares, and views are all taken into account. 📈📉")

c, df = appUtils.get_chart()
st.altair_chart(c, use_container_width=True)

df = df[["source", "timestamp", "engagement_score", "total_comments", "total_views", "total_likes", "total_followers"]].rename(columns={
    "timestamp": "Date",
    "source": "Source",
    "engagement_score": "Engagement Score",
    "total_comments":"Total Comments",
    "total_views":"Total Views",
    "total_likes":"Total Likes",
    "total_followers":"Total Followers"
})
st.header("Data")
for source in df["Source"].unique().tolist():
    st.write(source)
    st.dataframe(df.loc[df["Source"]==source].set_index("Date").sort_values("Date", ascending=False), use_container_width=True)

st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.divider()
st.header("Survey")
with st.form("my_form"):
        st.write("Still validating this idea, let me know what you think! 🧪📊")
        answer_interest = st.text_input("Any suggestions?", key="answer_interest")
        answer_price = st.number_input("How much would you pay for a service like this? (USD)", min_value=0, key="answer_price")
        email = st.text_input("Would you like to receive launch updates via email? Enter your email address below!", key="email")
        submitted = st.form_submit_button("Submit", on_click=appUtils.on_click, args=[appUtils])
