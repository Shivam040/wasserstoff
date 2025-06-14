import streamlit as st
import requests
import pandas as pd
import re

import os
API_URL = os.getenv("BACKEND_URL", "https://wasserstoff-5-sv55.onrender.com")

# Configure the Streamlit page title and layout
st.set_page_config(page_title="Gen-AI Chatbot", layout="wide")
st.title("📚 Document Theme Identifier Chatbot")

# Track uploaded docs in session state
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = set()

# Sidebar upload widget allowing the user to upload files
st.sidebar.title("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF, text, or image file", type=["pdf", "txt", "jpg", "png", "jpeg"])

# When a file is uploaded, it is sent as multipart form data to the /upload/ endpoint of the FastAPI backend.
if uploaded_file:
    with st.spinner("Uploading and processing..."):
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{API_URL}/upload/", files=files)
        if response.status_code == 200:
            result = response.json()
            st.session_state.uploaded_docs.add(result["filename"])
            st.sidebar.success(f"Uploaded: {result['filename']}")
        else:
            try:
                error_details = response.json()
            except Exception:
                error_details = response.text
            st.sidebar.error(f"Upload failed. Status code: {response.status_code}, Details: {error_details}")


st.markdown("---")

query = st.text_input("🔍 Ask a question about the documents")
# Document Selection
st.subheader("📂 Select documents to include in query")

# Display checkboxes for all uploaded documents, defaulting to checked.
if not st.session_state.uploaded_docs:
    st.info("Upload some documents first.")
else:
    # Show a checkbox for each uploaded document
    selected_files = []
    for doc in sorted(st.session_state.uploaded_docs):
        if st.checkbox(doc, value=True):
            selected_files.append(doc)

# Query Submission and Answer Display
if st.button("Get Answer"):
    if not query.strip():
        st.warning("Please enter a question.")
    elif not selected_files:
        st.warning("Please select at least one document.")
    else:
        with st.spinner("Querying backend..."):
            response = requests.post(
                f"{API_URL}/query/",
                data={"query": query, "selected_docs": selected_files}
            )
            # Display Document Answers
            if response.status_code == 200:
                result = response.json()


                answers = result.get("individual_answers", [])
                if answers:
                    st.subheader("📄 Document Answers (Tabular View)")
                    
                    # Build a DataFrame for clean table
                    df = pd.DataFrame([
                        {
                            "Document ID": ans["doc_id"],
                            "Extracted Answer": ans["answer"],
                            "Citation": ans["citation"]
                        }
                        for ans in answers
                    ])
                    # Style the table
                    styled_df = df.style.set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'left')]},
                        {'selector': 'td', 'props': [('text-align', 'left'), ('max-width', '250px')]},  # All cells
                        {'selector': 'td.col0', 'props': [('min-width', '120px')]},  # Document ID
                        {'selector': 'td.col2', 'props': [('min-width', '120px')]},  # Citation
                    ]).set_properties(**{
                        'white-space': 'pre-wrap',  # Wrap long text instead of overflowing
                    })

                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.write("_No document answers returned._")


                # Display Themes
                themes = result.get("themes", [])
                if themes:
                    st.subheader("🧠 Synthesized Themes")
                    for i, t in enumerate(themes, start=1):
                        st.markdown(f"**Theme {i} – {t['theme']}:**")
                        st.markdown(f"{t['supporting_docs']}: {t['description']}")
                        st.markdown("---")
                else:
                    st.write("_No themes identified._")


            else:
                st.error("Something went wrong. Check backend logs.")
