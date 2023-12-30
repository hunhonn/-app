from deta import Deta
import os
import streamlit as st
#from dotenv import load_dotenv

#load_dotenv(".env")
db_token=st.secrets["db_token"]

deta=Deta(db_token)

db=deta.Base("currency_db")

def fetch_all():
    res=db.fetch()
    return res.items

