import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SilatGuide",
    page_icon="🥋",
    layout="centered"
)

# Chatbot title
st.title("🥋 SilatGuide")
st.caption("Your AI Silat Learning Assistant")

# Welcome message
st.info(
    "Welcome to SilatGuide! Ask me anything about "
    "Silat history, techniques, and traditions."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Clear chats
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about Silat..."):

    # Display user's message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Temporary response until backend is connected
    with st.chat_message("assistant"):
        response = (
            "Thank you for your question! "
            "The SilatGuide AI model will be connected soon."
        )
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })