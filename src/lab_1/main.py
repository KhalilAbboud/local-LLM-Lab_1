import streamlit as st
import ollama

MODEL = "smallthinker:3b"
DEFAULT_SYSTEM_PROMPT = "You are a helpful and concise assistant."

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

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.write(f"**Model:** `{MODEL}`")
    st.write("**Backend:** Ollama")
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
    )
    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=140,
        help="Instructions sent to the model before the conversation starts.",
    )

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
            system_prompt = (
                st.session_state.system_prompt.strip()
                if st.session_state.system_prompt and st.session_state.system_prompt.strip()
                else DEFAULT_SYSTEM_PROMPT
            )
            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(st.session_state.messages)

            stream = ollama.chat(
                model=MODEL,
                messages=api_messages,
                stream=True,
                options={"temperature": st.session_state.temperature},
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
