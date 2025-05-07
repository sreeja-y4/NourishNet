import streamlit as st
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# -------------------- Streamlit App Setup --------------------

st.set_page_config(page_title="NourishNet - UMD Pantry", layout="centered")
st.title("NourishNet: UMD Pantry Inventory - Image Upload")

# -------------------- Load Model --------------------

# Make sure 'models/best.pt' exists in your repo
model = YOLO("models/best.pt")

# -------------------- Connect to Google Sheets --------------------

# Using secrets stored securely in Streamlit Cloud
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets"], scope)
client = gspread.authorize(creds)
sheet = client.open("NourishNet Confirmations").sheet1  # Must match your Sheet name

# -------------------- Optional Dietary Tags --------------------

dietary_tags = {
    "Canned Beans": ["vegan", "gluten-free"],
    "Milk": ["vegetarian"],
    "Bread": ["vegetarian"],
    "Chicken Breast": ["halal"],
    "Tofu": ["vegan"],
    # Add more as needed
}

# -------------------- Image Upload Interface --------------------

uploaded_file = st.file_uploader("📤 Upload a pantry image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # -------------------- Run YOLOv8 Detection --------------------
    with st.spinner("🔍 Detecting items..."):
        results = model.predict(image)
        result_image = results[0].plot()
        detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
        counts = Counter(detected_classes)

    if counts:
        st.subheader("✅ Detected Items")
        for item, count in counts.items():
            st.write(f"- {item}: {count}")

        st.image(result_image, caption="Detected Items", use_column_width=True)

        if st.button("📝 Confirm & Save to Pantry Log"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for item, count in counts.items():
                tags = ", ".join(dietary_tags.get(item, []))  # Match optional tags
                sheet.append_row([timestamp, "UMD Campus Pantry", item, count, tags])
            st.success("✔️ Items saved to NourishNet Sheet!")
    else:
        st.warning("⚠️ No items detected. Try a clearer image.")
else:
    st.info("👈 Upload an image to begin.")

