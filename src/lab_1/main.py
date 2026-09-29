import streamlit as st
import ollama

MODEL = "smallthinker:3b"
DEFAULT_SYSTEM_PROMPT = "You are a helpful and concise assistant that talks less."
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

# The palette lives in .streamlit/config.toml so Streamlit themes its own
# widgets. This stylesheet only covers what the theme cannot reach: chat
# bubbles, the chat composer, rendered markdown, scrollbars and hover/focus
# feedback. Every token below is defined once and reused.
st.markdown(
    """
    <style>
        /* ---------- design tokens ---------- */
        :root {
            --sidebar-bg: #0a1830;
            --line: rgba(160, 189, 255, 0.16);
            --line-strong: rgba(160, 189, 255, 0.32);
            --primary: #8bb4ff;
            --primary-strong: #5d8ef7;
            --on-primary: #06152a;
            --text: #edf4ff;
            --muted: #a9bcd9;
            --bubble-user: #143a63;
            --bubble-assistant: #102b46;
            --code-bg: #061426;
            --radius: 14px;
            --shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
            --font: "Inter", "Segoe UI", system-ui, -apple-system,
                    "Helvetica Neue", Arial, sans-serif;
            --mono: "JetBrains Mono", "Cascadia Code", "SF Mono", Consolas,
                    "Liberation Mono", monospace;
            --speed: 150ms ease;
        }

        /* ---------- base typography ---------- */
        html, body, .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            font-family: var(--font);
            color: var(--text);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text);
            font-weight: 650;
            letter-spacing: -0.01em;
        }

        /* Streamlit 1.64 renders headings as .stHeading, not .stTitle. */
        [data-testid="stHeading"] {
            margin-bottom: 0.1rem;
        }

        .stCaption,
        [data-testid="stCaptionContainer"] {
            color: var(--muted);
        }

        a {
            color: var(--primary);
            text-decoration: none;
            transition: color var(--speed);
        }

        a:hover {
            color: #ffffff;
            text-decoration: underline;
        }

        /* header rule under the title block */
        hr,
        [data-testid="stMarkdownContainer"] hr {
            border: none;
            border-top: 1px solid var(--line);
            margin: 0.9rem 0 1rem;
        }

        /* ---------- sidebar ----------
           Width is intentionally left to Streamlit. Forcing width/min-width/
           max-width with !important blocks the collapse animation, which
           leaves stSidebarCollapseButton and the collapsed-state expand
           control both visible at the same time. */
        [data-testid="stSidebar"] {
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background: var(--sidebar-bg) !important;
            padding: 0.9rem 0.9rem 1.4rem;
        }

        [data-testid="stSidebarHeader"] button {
            color: var(--muted);
            transition: color var(--speed);
        }

        [data-testid="stSidebarHeader"] button:hover {
            color: var(--text);
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stNumberInput,
        [data-testid="stSidebar"] .stTextArea,
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stCheckbox {
            font-size: 0.88rem;
        }

        /* ---------- sidebar controls ---------- */
        [data-testid="stSidebar"] .stTextInput > div,
        [data-testid="stSidebar"] .stTextArea > div,
        [data-testid="stSidebar"] .stNumberInput > div,
        [data-testid="stSidebar"] .stSlider > div,
        [data-testid="stSidebar"] .stSelectbox > div,
        [data-testid="stSidebar"] .stCheckbox > div {
            border-radius: 10px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.02);
            transition: border-color var(--speed),
                        background var(--speed),
                        box-shadow var(--speed);
        }

        [data-testid="stSidebar"] .stTextInput > div:focus-within,
        [data-testid="stSidebar"] .stTextArea > div:focus-within,
        [data-testid="stSidebar"] .stNumberInput > div:focus-within,
        [data-testid="stSidebar"] .stSelectbox > div:focus-within {
            border-color: var(--primary-strong);
            background: rgba(93, 142, 247, 0.06);
            box-shadow: 0 0 0 1px rgba(93, 142, 247, 0.35);
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] .stNumberInput input {
            background: transparent;
            color: var(--text);
            font-family: var(--font);
            caret-color: var(--primary);
            outline: none;
        }

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: var(--muted);
            opacity: 0.75;
        }

        [data-testid="stSidebar"] .stSlider {
            margin-top: 0.1rem;
            margin-bottom: 0.2rem;
        }

        [data-testid="stSidebar"] .stNumberInput > div > div {
            display: flex;
            align-items: center;
        }

        /* Sliders are rendered by react-aria in 1.64, so the old
           "data-baseweb" and "stBaseSlider" selectors no longer match. */
        [data-testid="stSlider"] .react-aria-Slider {
            margin: 0.4rem 0 0.6rem;
        }

        [data-testid="stSlider"] .react-aria-SliderTrack {
            background: rgba(160, 189, 255, 0.18);
            border: none;
            border-radius: 999px;
            height: 5px;
            transition: background var(--speed);
        }

        [data-testid="stSlider"] .react-aria-SliderTrack:hover {
            background: rgba(160, 189, 255, 0.28);
        }

        [data-testid="stSlider"] .react-aria-SliderThumb {
            background: var(--primary);
            border: 2px solid var(--sidebar-bg);
            border-radius: 50%;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.55);
            transition: transform var(--speed), box-shadow var(--speed);
        }

        [data-testid="stSlider"] .react-aria-SliderThumb:hover,
        [data-testid="stSlider"] .react-aria-SliderThumb[data-hovered] {
            transform: scale(1.15);
        }

        [data-testid="stSlider"] .react-aria-SliderThumb[data-dragging] {
            transform: scale(1.25);
            box-shadow: 0 0 0 6px rgba(93, 142, 247, 0.18);
        }

        [data-testid="stSlider"] .react-aria-SliderThumb[data-focus-visible] {
            box-shadow: 0 0 0 3px rgba(93, 142, 247, 0.55);
        }

        [data-testid="stSliderThumbValue"] {
            background: var(--primary);
            color: var(--on-primary);
            font-weight: 650;
            font-size: 0.7rem;
            border-radius: 6px;
        }

        /* number input steppers */
        [data-testid="stNumberInputStepUp"],
        [data-testid="stNumberInputStepDown"] {
            background: rgba(255, 255, 255, 0.05);
            color: var(--muted);
            border-radius: 6px;
            transition: background var(--speed), color var(--speed);
        }

        [data-testid="stNumberInputStepUp"]:hover,
        [data-testid="stNumberInputStepDown"]:hover {
            background: var(--primary-strong);
            color: var(--on-primary);
        }

        /* ---------- buttons ---------- */
        .stButton > button {
            width: 100%;
            background: linear-gradient(180deg, #1d4373 0%, #173457 100%);
            color: var(--text);
            border: 1px solid var(--line-strong);
            border-radius: 10px;
            padding: 0.45rem 0.8rem;
            font-family: var(--font);
            font-weight: 600;
            box-shadow: var(--shadow);
            transition: filter var(--speed),
                        border-color var(--speed),
                        transform 100ms ease;
        }

        .stButton > button:hover {
            filter: brightness(1.2);
            border-color: var(--primary);
        }

        .stButton > button:active {
            transform: translateY(1px);
        }

        .stButton > button:focus-visible {
            outline: 2px solid var(--primary-strong);
            outline-offset: 2px;
        }

        /* ---------- chat messages ---------- */
        [data-testid="stChatMessage"] {
            background: transparent;
            border: none;
            box-shadow: none;
            padding: 0.15rem 0;
        }

        [data-testid="stChatMessageContent"],
        [data-testid="stChatMessage"] > div:last-child {
            background: var(--bubble-assistant);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 0.65rem 0.9rem;
            box-shadow: var(--shadow);
            min-width: 0;
            overflow-wrap: anywhere;
        }

        /* NOTE: the avatar test ids in Streamlit are "AvatarUser" and
           "AvatarAssistant". The earlier "chatAvatarUser" spelling never
           matched, which left user and assistant bubbles looking identical. */
        [data-testid="stChatMessage"]:has([data-testid="AvatarUser"])
            [data-testid="stChatMessageContent"],
        [data-testid="stChatMessage"]:has([data-testid="AvatarUser"])
            > div:last-child {
            background: var(--bubble-user);
            border-color: rgba(139, 180, 255, 0.28);
            border-left: 3px solid var(--primary-strong);
        }

        /* Avatar circles are left at Streamlit's default size. */

        /* ---------- rendered markdown inside replies ---------- */
        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessage"] > div:last-child p {
            line-height: 1.6;
            margin-bottom: 0.6rem;
        }

        [data-testid="stChatMessageContent"] > *:last-child,
        [data-testid="stChatMessage"] > div:last-child > *:last-child {
            margin-bottom: 0;
        }

        [data-testid="stChatMessageContent"] ul,
        [data-testid="stChatMessageContent"] ol {
            padding-left: 1.2rem;
            margin-bottom: 0.6rem;
        }

        [data-testid="stChatMessageContent"] li {
            margin-bottom: 0.25rem;
            line-height: 1.55;
        }

        [data-testid="stChatMessageContent"] blockquote {
            border-left: 3px solid var(--primary-strong);
            background: rgba(93, 142, 247, 0.08);
            color: var(--muted);
            margin: 0.5rem 0;
            padding: 0.35rem 0.85rem;
            border-radius: 0 8px 8px 0;
        }

        [data-testid="stChatMessageContent"] hr {
            border-top: 1px solid var(--line);
            margin: 0.9rem 0;
        }

        [data-testid="stChatMessageContent"] table {
            border-collapse: collapse;
            width: 100%;
            font-size: 0.88rem;
            margin: 0.5rem 0;
        }

        [data-testid="stChatMessageContent"] th,
        [data-testid="stChatMessageContent"] td {
            border: 1px solid var(--line);
            padding: 0.4rem 0.65rem;
            text-align: left;
        }

        [data-testid="stChatMessageContent"] th {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text);
            font-weight: 650;
        }

        [data-testid="stChatMessageContent"] tbody tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.02);
        }

        /* code inside replies */
        [data-testid="stChatMessageContent"] code,
        [data-testid="stChatMessage"] > div:last-child code {
            background: var(--code-bg);
            color: #cfe3ff;
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: 0.1rem 0.35rem;
            font-family: var(--mono);
            font-size: 0.85em;
        }

        [data-testid="stCode"] {
            background: var(--code-bg);
            border: 1px solid var(--line);
            border-radius: 10px;
        }

        [data-testid="stCode"] code {
            background: transparent;
            border: none;
            padding: 0;
            color: #d6e6ff;
            font-family: var(--mono);
        }

        pre {
            background: var(--code-bg);
            border: 1px solid var(--line);
            border-radius: 10px;
        }

        pre code {
            background: transparent;
            border: none;
            padding: 0;
        }

        /* ---------- chat composer ----------
           The composer is left entirely to Streamlit's native theme. It
           already renders the mic, file-upload and send controls correctly;
           restyling it produced a stray circular button in the pill. */

        /* ---------- chrome ---------- */
        [data-testid="stHeader"] {
            background: transparent;
        }

        /* The scroll-to-bottom control keeps Streamlit's default shape. */

        [data-testid="stSpinner"] > div > div {
            border-top-color: var(--primary);
        }

        .stTooltip {
            background: #0f2743;
            border: 1px solid var(--line-strong);
            color: var(--text);
        }

        /* ---------- scrollbars ---------- */
        * {
            scrollbar-width: thin;
            scrollbar-color: rgba(160, 189, 255, 0.28) transparent;
        }

        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(160, 189, 255, 0.24);
            border: 2px solid transparent;
            border-radius: 999px;
            background-clip: content-box;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(160, 189, 255, 0.45);
            background-clip: content-box;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SmallThinker Chatbot")
st.caption(f"Powered locally by Ollama • {MODEL}")
st.markdown("---")

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
