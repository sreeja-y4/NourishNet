import streamlit as st
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os

st.set_page_config(page_title="NourishNet - UMD Pantry Inventory Detector", layout="centered")
st.title("NourishNet - UMD Pantry Inventory Detector")

# Load YOLOv8 model
model = YOLO("models/best.pt")

# Set up credentials for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "google_sheets" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets"], scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials/nourishnet-creds.json", scope)

client = gspread.authorize(creds)
sheet = client.open("NourishNet Confirmations").sheet1

# Dietary logic
def infer_tags(item_name):
    name = item_name.lower()
    tags = []

    if not any(word in name for word in ["chicken", "beef", "pork", "meat", "fish"]):
        tags.append("vegetarian")

        if not any(word in name for word in ["milk", "cheese", "yogurt", "egg"]):
            tags.append("vegan")

    if not any(word in name for word in ["bread", "pasta", "wheat", "bun", "carbohydrate meal"]): 
        tags.append("gluten-free")

    return ", ".join(tags) if tags else "unclassified"

# UI
uploaded_file = st.file_uploader("Please upload an image of the pantry or fridge", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    results = model.predict(image)
    result_image = results[0].plot()
    detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
    counts = Counter(detected_classes)

    if counts:
        st.subheader("Detected Items & Dietary Tags")
        for item, count in counts.items():
            tags = infer_tags(item)
            st.write(f"- {item}: {count} → Tags: `{tags}`")

        if st.button("Confirm & Save to Pantry Log"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for item, count in counts.items():
                tags = infer_tags(item)
                sheet.append_row([timestamp, "UMD Campus Pantry", item, count, tags])
            st.success("All items saved with dietary tags!")
    else:
        st.warning("No items detected. Try a clearer image.")
