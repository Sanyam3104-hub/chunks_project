import streamlit as st
import requests

st.title("📄 PDF Chunker App")

FASTAPI_URL = "http://127.0.0.1:8000"

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

# Track upload status
if "upload_success" not in st.session_state:
    st.session_state.upload_success = False

# Upload PDFs
if uploaded_files:
    files = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
    if st.button("Upload to Server"):
        try:
            res = requests.post(f"{FASTAPI_URL}/upload_pdfs/", files=files)
            if res.status_code == 200:
                st.success("✅ Files uploaded successfully!")
                st.session_state.upload_success = True
            else:
                st.error(f"❌ Upload failed: {res.status_code}")
        except Exception as e:
            st.error(f"🚫 Upload Error: {e}")

# Create Chunks (only after upload)
if st.session_state.upload_success:
    if st.button("Create Chunks"):
        try:
            st.info("📦 Creating chunks... Please wait")
            chunk_res = requests.post(f"{FASTAPI_URL}/create_chunks/")
            if chunk_res.status_code == 200:
                st.success("✅ Chunks created successfully!")
                chunks = chunk_res.json()
                for filename, data in chunks.items():
                    st.subheader(f"📘 {filename}")
                    for method, chunk_map in data["chunks_by_technique"].items():
                        st.markdown(f"### 🔹 {method}")
                        for chunk_id, text in chunk_map.items():
                            with st.expander(chunk_id):
                                st.write(text)
            else:
                st.error(f"❌ Error creating chunks: {chunk_res.status_code}")
        except Exception as e:
            st.error(f"🚫 Chunking Error: {e}")
