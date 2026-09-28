import streamlit as st
import ollama

MODEL = "smallthinker:3b"

st.set_page_config(
    page_title="SmallThinker Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 SmallThinker Chatbot")
st.caption(f"Powered locally by Ollama • {MODEL}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm SmallThinker running locally through Ollama. How can I help?",
        }
    ]

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.write(f"**Model:** `{MODEL}`")
    st.write("**Backend:** Ollama")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat cleared. What would you like to talk about?",
            }
        ]
        st.rerun()

# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            stream = ollama.chat(
                model=MODEL,
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                full_response += token
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        except ollama.ResponseError as e:
            full_response = (
                f"**Ollama error:** `{e}`\n\n"
                f"Make sure the model is installed with:\n\n"
                f"`ollama pull {MODEL}`"
            )
            response_placeholder.error(full_response)

        except Exception as e:
            full_response = (
                "**Could not connect to Ollama.**\n\n"
                "Make sure Ollama is running, then try again.\n\n"
                f"Error: `{e}`"
            )
            response_placeholder.error(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
