import streamlit as st
import requests
import json

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Seven Moving AI Assistant",
    page_icon="🚚",
    layout="wide"
)

# ============================================
# CUSTOM STYLING
# ============================================

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }

    .subtitle {
        font-size: 16px;
        color: #B0B0B0;
        margin-bottom: 30px;
    }

    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
    }

    div[data-testid="stChatInput"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# API CONFIGURATION
# ============================================

API_URL = "http://localhost:7071/api/rag"

# ============================================
# SESSION STATE
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:

    st.header("🚚 Seven Moving")

    st.write("AI-powered company knowledge assistant")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Powered by Azure OpenAI + Azure AI Search")

# ============================================
# MAIN HEADER
# ============================================

st.title("🚚 Seven Moving AI Assistant")

st.write(
    "Ask me anything about Seven Moving services, "
    "pricing, policies, and moving procedures."
)

st.divider()

# ============================================
# DISPLAY CHAT HISTORY
# ============================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                with st.expander(
                    f"📚 Source References ({len(sources)})"
                ):

                    for i, source in enumerate(sources, start=1):

                        st.markdown(f"### Source {i}")

                        if isinstance(source, dict):

                            source_id = source.get(
                                "id", "Unknown"
                            )

                            source_title = source.get(
                                "title",
                                source.get("filename", "Company Document")
                            )

                            source_content = source.get(
                                "content", "No preview available."
                            )

                            st.write(f"**Document:** {source_title}")

                            st.write(f"**Chunk ID:** {source_id}")

                            st.write("**Relevant document content:**")

                            st.info(source_content)

                            source_url = source.get("url")

                            if source_url:
                                st.markdown(
                                    f"[Open source document]({source_url})"
                                )

                        else:

                            st.write(f"**Chunk ID:** {source}")

                            st.caption(
                                "Detailed source information is "
                                "not yet available from the API."
                            )

                        st.divider()

# ============================================
# USER INPUT
# ============================================

question = st.chat_input(
    "Ask a question about Seven Moving..."
)

if question:

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # ========================================
    # CALL AZURE FUNCTION API
    # ========================================

    with st.chat_message("assistant"):

        with st.spinner("Searching company documents..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question
                    },
                    timeout=60
                )

                response.raise_for_status()

                data = response.json()

                # Extract answer
                answer = data.get(
                    "answer",
                    "Sorry, I couldn't find an answer."
                )

                # Extract source references
                sources = data.get("sources", [])

                # Backward compatibility
                if not sources:
                    sources = data.get("chunks_used", [])

                # Display answer
                st.markdown(answer)

                # Display sources
                if sources:

                    with st.expander(
                        f"📚 Source References ({len(sources)})"
                    ):

                        for i, source in enumerate(
                            sources, start=1
                        ):

                            st.markdown(f"### Source {i}")

                            if isinstance(source, dict):

                                source_id = source.get(
                                    "id", "Unknown"
                                )

                                source_title = source.get(
                                    "title",
                                    source.get(
                                        "filename",
                                        "Company Document"
                                    )
                                )

                                source_content = source.get(
                                    "content",
                                    "No preview available."
                                )

                                st.write(
                                    f"**Document:** {source_title}"
                                )

                                st.write(
                                    f"**Chunk ID:** {source_id}"
                                )

                                st.write(
                                    "**Relevant document content:**"
                                )

                                st.info(source_content)

                                source_url = source.get("url")

                                if source_url:
                                    st.markdown(
                                        f"[Open source document]({source_url})"
                                    )

                            else:

                                st.write(
                                    f"**Chunk ID:** {source}"
                                )

                                st.caption(
                                    "Detailed source information "
                                    "is not yet available from the API."
                                )

                            st.divider()

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to Azure Functions. "
                    "Make sure 'func start' is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. Please try again."
                )

            except requests.exceptions.HTTPError as e:

                st.error(
                    f"API returned an error: {str(e)}"
                )

            except json.JSONDecodeError:

                st.error(
                    "The API returned an invalid JSON response."
                )

            except Exception as e:

                st.error(
                    f"Unexpected error: {str(e)}"
                )