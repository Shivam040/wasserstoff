import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Gen-AI Chatbot", layout="wide")
st.title("📚 Document Theme Identifier Chatbot")

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = set()


st.sidebar.title("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF, text, or image file", type=["pdf", "txt", "jpg", "png", "jpeg"])

if uploaded_file:
    with st.spinner("Uploading and processing..."):
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{API_URL}/upload/", files=files)
        if response.status_code == 200:
            result = response.json()
            st.session_state.uploaded_docs.add(result["filename"])
            st.sidebar.success(f"Uploaded: {result['filename']}")
        else:
            st.sidebar.error(f"Upload failed: {response.json()}")


st.markdown("---")

query = st.text_input("🔍 Ask a question about the documents")

st.subheader("📂 Select documents to include in query")

if not st.session_state.uploaded_docs:
    st.info("Upload some documents first.")
else:
    selected_files = []
    for doc in sorted(st.session_state.uploaded_docs):
        if st.checkbox(doc, value=True):
            selected_files.append(doc)


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

                    st.table(df)
                else:
                    st.write("_No document answers returned._")


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
