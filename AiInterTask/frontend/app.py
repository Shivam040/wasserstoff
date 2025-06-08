import streamlit as st
import requests

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

                # st.subheader("🧠 Synthesized Answer")
                # st.markdown(result.get("synthesized_answer", "_No answer returned._"))

                st.subheader("📄 Individual Document Answers")
                answers = result.get("individual_answers", [])
                if answers:
                    for ans in answers:
                        st.markdown(f"**{ans['doc_id']}** - {ans['citation']}")
                        st.write(ans['answer'])
                        st.markdown("---")
                else:
                    st.write("_No document answers returned._")

                st.subheader("🔎 Identified Themes")
                themes = result.get("themes", [])
                if themes:
                    for t in themes:
                        st.markdown(f"**Theme**: {t['theme']}")
                        st.write("Supporting Docs:", ", ".join(t['supporting_docs']))
                        st.markdown("---")
                else:
                    st.write("_No themes identified._")

            else:
                st.error("Something went wrong. Check backend logs.")


# import streamlit as st
# import requests

# st.set_page_config(page_title="Wasserstoff LLM", layout="wide")

# st.title("📄 Document Q&A + Theme Extractor")

# query = st.text_input("Enter your query:")

# if st.button("Submit Query") and query:
#     with st.spinner("Querying backend..."):
#         response = requests.post(
#             "http://localhost:8000/query/",
#             data={"query": query}  # because FastAPI expects `Form(...)`
#         )

#         if response.status_code == 200:
#             data = response.json()

#             st.subheader("🧠 Synthesized Answer")
#             st.markdown(data["synthesized_answer"])

#             st.subheader("📚 Individual Document Answers")
#             for ans in data["individual_answers"]:
#                 st.markdown(f"**Doc ID**: {ans['doc_id']}")
#                 st.markdown(f"**Answer**: {ans['answer']}")
#                 st.markdown(f"**Citation**: {ans['citation']}")
#                 st.markdown("---")

#             st.subheader("🎯 Themes")
#             for theme in data["themes"]:
#                 st.markdown(f"**Theme**: {theme['theme']}")
#                 st.markdown(f"**Supporting Docs**: {', '.join(theme['supporting_docs'])}")
#                 st.markdown("---")

#         else:
#             st.error("Failed to fetch response from the backend.")
