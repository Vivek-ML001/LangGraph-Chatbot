import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_backend import chatbot, retrive_all_thread

st.set_page_config(page_title="Langgraph Chatbot", page_icon="✨", layout="centered")

USER_NAME = "Vivek"

# ---------------- Gemini-style CSS ----------------
st.markdown("""
<style>
#MainMenu, footer, header[data-testid="stHeader"] {background: transparent;}
footer {visibility: hidden;}

/* Background gradient */
.stApp {
    background: radial-gradient(ellipse at 70% 80%, #cfe3fb 0%, #e8f0fc 35%, #ffffff 75%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f0f4f9;
    border-right: none;
}
[data-testid="stSidebar"] h1 {font-size: 1.3rem; font-weight: 500;}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 0.85rem; font-weight: 500; color: #444746; margin-top: 1rem;
}
[data-testid="stSidebar"] button {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
    border: none;
    border-radius: 999px;
    background: transparent;
    color: #1f1f1f;
    padding: 0.45rem 1rem;
    box-shadow: none;
}
[data-testid="stSidebar"] button:hover {background: #e1e7ef;}
/* Active chat highlight */
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background: #d3e3fd;
    color: #041e49;
    font-weight: 500;
}

/* Greeting */
.greet-wrap {text-align: center; margin-top: 18vh; margin-bottom: 2rem;}
.greet-hi {
    font-size: 2.6rem; font-weight: 500;
    background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.greet-q {font-size: 2.6rem; font-weight: 400; color: #444746; margin-top: -0.3rem;}

/* Suggestion chips (main area buttons) */
section.main .stButton > button, [data-testid="stMain"] .stButton > button {
    border-radius: 999px;
    border: 1px solid #dde3ea;
    background: rgba(255,255,255,0.8);
    color: #1f1f1f;
    padding: 0.55rem 1.1rem;
    width: 100%;
}
[data-testid="stMain"] .stButton > button:hover {background: #e9eef6; border-color: #c4d0e0;}

/* Hide avatars */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {display: none;}

/* Messages */
[data-testid="stChatMessage"] {background: transparent; padding: 0.4rem 0;}
/* User bubble, right aligned */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: #e9eef6;
    border-radius: 22px;
    padding: 0.7rem 1.1rem;
    max-width: 75%;
    width: fit-content;
}

/* Chat input pill */
[data-testid="stChatInput"] {
    border-radius: 32px;
    background: #ffffff;
    border: none;
    box-shadow: 0 2px 10px rgba(60,64,67,0.15);
    padding: 0.25rem 0.5rem;
}
[data-testid="stChatInput"] textarea {font-size: 1.05rem;}
[data-testid="stBottom"] > div {background: transparent;}
</style>
""", unsafe_allow_html=True)


# ---------------- Helpers ----------------
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def get_thread_title(thread_id):
    for mesg in load_conversation(thread_id):
        if isinstance(mesg, HumanMessage):
            return mesg.content
    return f"New chat {thread_id[:6]}"

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []


# ---------------- Session state ----------------
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrive_all_thread()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if not st.session_state['chat_thread']:
    new_id = generate_thread_id()
    st.session_state['thread_id'] = new_id
    add_thread(new_id)

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = st.session_state['chat_thread'][0]

if 'pending_prompt' not in st.session_state:
    st.session_state['pending_prompt'] = None


# ---------------- Sidebar ----------------
st.sidebar.title('✨ Langgraph Chatbot')

if st.sidebar.button('✏️  New chat', key='new_chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('Recent')

for thread_id in reversed(st.session_state['chat_thread']):
    title = get_thread_title(thread_id)
    display_title = title[:26] + ("..." if len(title) > 26 else "")
    is_active = thread_id == st.session_state['thread_id']

    if st.sidebar.button(
        display_title,
        key=thread_id,
        type="primary" if is_active else "secondary",
    ):
        st.session_state['thread_id'] = thread_id
        temp_message = []
        for mesg in load_conversation(thread_id):
            if isinstance(mesg, HumanMessage):
                role = 'user'
            elif isinstance(mesg, AIMessage):
                role = 'assistant'
            else:
                continue
            temp_message.append({'role': role, 'content': mesg.content})
        st.session_state['message_history'] = temp_message
        st.rerun()


# ---------------- Main area ----------------
# Empty state: greeting + suggestion chips
if not st.session_state['message_history']:
    st.markdown(
        f"""
        <div class="greet-wrap">
            <div class="greet-hi">Hello, {USER_NAME}</div>
            <div class="greet-q">Where should we start?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        "💡 Explain a concept simply",
        "💻 Help me debug my code",
        "📝 Summarize some text",
        "🚀 Give me project ideas",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sugg_{i}"):
            st.session_state['pending_prompt'] = s.split(" ", 1)[1]
            st.rerun()

# Chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# ---------------- Input ----------------
user_input = st.chat_input('Ask Gemini-style... type here')

if not user_input and st.session_state['pending_prompt']:
    user_input = st.session_state['pending_prompt']
    st.session_state['pending_prompt'] = None

if user_input:
    current_thread = st.session_state['thread_id']

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': current_thread}}

    with st.chat_message('assistant'):
        with st.spinner("Thinking..."):
            response = chatbot.invoke(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
            )
        ai_message = response['messages'][-1].content
        st.markdown(ai_message)

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()
