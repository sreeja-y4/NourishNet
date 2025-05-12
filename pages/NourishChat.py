import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Page setup
st.set_page_config(page_title="NourishChat - Filter by Dietary Need", layout="centered")
st.title("🍎 NourishChat: Pantry Items by Dietary Filter")

# Connect to Google Sheets via Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets"], scope)
client = gspread.authorize(creds)
sheet = client.open("NourishNet Confirmations").sheet1

data = sheet.get_all_records()
df = pd.DataFrame(data)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

today = datetime.now().strftime("%Y-%m-%d")
df_today = df[df["timestamp"].str.startswith(today)]

option = st.radio("🥗 What is your dietary preference?", ["vegan", "vegetarian", "gluten-free"])

filtered = df_today[df_today["dietary tags"].str.contains(option, case=False, na=False)]

if not filtered.empty:
    st.success(f"Items available today for a **{option}** diet:")
    for _, row in filtered.iterrows():
        st.write(f"- {row['item']} (x{row['quantity']})")
else:
    st.warning(f"No items found today with the tag '{option}'.")
