import streamlit as st
import ollama

MODEL = "smallthinker:3b"
DEFAULT_SYSTEM_PROMPT = "You are a helpful and concise assistant."
DEFAULT_OPTIONS = {
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "min_p": 0.0,
    "repeat_penalty": 1.1,
    "repeat_last_n": 64,
    "seed": 42,
    "num_ctx": 2048,
    "num_predict": 256,
    "stop": "",
}

st.set_page_config(
    page_title="SmallThinker Chatbot",
    page_icon="✨",
    layout="centered",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #071a2f;
            --panel: #0d2340;
            --panel-soft: #122d4c;
            --line: rgba(160, 189, 255, 0.18);
            --primary: #8bb4ff;
            --primary-strong: #5d8ef7;
            --text: #edf4ff;
            --muted: #b8c9e6;
            --bubble-user: #143a63;
            --bubble-assistant: #102b46;
            --button: #1b3c63;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #061624 0%, #0b1d33 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: rgba(9, 22, 38, 0.95);
            border-right: 1px solid var(--line);
        }

        .stApp {
            color: var(--text);
        }

        h1, h2, h3 {
            color: var(--text) !important;
            letter-spacing: 0.02em;
        }

        .stTitle {
            margin-bottom: 0.25rem;
        }

        .stCaption {
            color: var(--muted) !important;
        }

        div[data-testid="stVerticalBlock"] > div {
            border-radius: 18px;
        }

        [data-testid="stChatMessage"] {
            border-radius: 18px;
            padding: 0.75rem 0.9rem;
            border: 1px solid var(--line);
            box-shadow: none;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarUser"]) {
            background: rgba(20, 58, 99, 0.85);
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarAssistant"]) {
            background: rgba(16, 43, 70, 0.9);
        }

        .stTextInput > div, .stTextArea > div, .stNumberInput > div, .stSlider > div {
            border-radius: 14px;
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--line);
        }

        .stButton > button {
            background: linear-gradient(180deg, #1d4373 0%, #173457 100%);
            color: var(--text);
            border: 1px solid rgba(170, 199, 255, 0.2);
            border-radius: 12px;
            padding: 0.6rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            border-color: rgba(170, 199, 255, 0.45);
            box-shadow: 0 10px 22px rgba(54, 100, 170, 0.2);
        }

        .stMarkdown {
            color: var(--text);
        }

        .stSidebar .stMarkdown {
            color: var(--text);
        }

        .stSidebar .stButton > button {
            width: 100%;
        }

        textarea, input {
            color: var(--text) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SmallThinker Chatbot")
st.caption(f"Powered locally by Ollama • {MODEL}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm SmallThinker running locally through Ollama. How can I help?",
        }
    ]

if "generation_options" not in st.session_state:
    st.session_state.generation_options = DEFAULT_OPTIONS.copy()

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.write(f"**Model:** `{MODEL}`")
    st.write("**Backend:** Ollama")

    st.session_state.generation_options["temperature"] = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.generation_options["temperature"],
        step=0.1,
    )
    st.session_state.generation_options["top_k"] = st.slider(
        "Top K",
        min_value=1,
        max_value=100,
        value=st.session_state.generation_options["top_k"],
        step=1,
    )
    st.session_state.generation_options["top_p"] = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.generation_options["top_p"],
        step=0.01,
    )
    st.session_state.generation_options["min_p"] = st.slider(
        "Min P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.generation_options["min_p"],
        step=0.01,
    )
    st.session_state.generation_options["repeat_penalty"] = st.slider(
        "Repeat Penalty",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.generation_options["repeat_penalty"],
        step=0.05,
    )
    st.session_state.generation_options["repeat_last_n"] = st.slider(
        "Repeat Last N",
        min_value=0,
        max_value=128,
        value=st.session_state.generation_options["repeat_last_n"],
        step=1,
    )
    st.session_state.generation_options["seed"] = st.number_input(
        "Seed",
        min_value=0,
        max_value=1000000,
        value=st.session_state.generation_options["seed"],
        step=1,
    )
    st.session_state.generation_options["num_ctx"] = st.number_input(
        "Context Window",
        min_value=128,
        max_value=32768,
        value=st.session_state.generation_options["num_ctx"],
        step=128,
    )
    st.session_state.generation_options["num_predict"] = st.number_input(
        "Max Tokens",
        min_value=32,
        max_value=4096,
        value=st.session_state.generation_options["num_predict"],
        step=32,
    )
    st.session_state.generation_options["stop"] = st.text_input(
        "Stop sequences",
        value=st.session_state.generation_options["stop"],
        help="Comma-separated values such as: \"\n\n\", \"###\"",
    )
    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=140,
        help="Instructions sent to the model before the conversation starts.",
    )

    if st.button("Clear chat", use_container_width=True):
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

            options = {
                key: value
                for key, value in st.session_state.generation_options.items()
                if value not in (None, "")
            }
            if isinstance(options.get("stop"), str):
                stop_values = [item.strip() for item in options["stop"].split(",") if item.strip()]
                options["stop"] = stop_values if stop_values else None

            stream = ollama.chat(
                model=MODEL,
                messages=api_messages,
                stream=True,
                options=options,
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
