import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_backend import chatbot, retrive_all_thread

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# Helper function to get thread title directly from saved checkpoint messages
def get_thread_title(thread_id):
    messages = load_conversation(thread_id)
    for mesg in messages:
        if isinstance(mesg, HumanMessage):
            # Use the first human message as title
            return mesg.content
    return f"Thread {thread_id[:6]}"

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

# 1. Initialize session states
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrive_all_thread()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Ensure at least one thread exists
if not st.session_state['chat_thread']:
    new_id = generate_thread_id()
    st.session_state['thread_id'] = new_id
    add_thread(new_id)

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = st.session_state['chat_thread'][0]

# 2. Sidebar setup
st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('My Conversation')

# Render sidebar buttons with title dynamically retrieved from database messages
for thread_id in st.session_state['chat_thread']:
    title = get_thread_title(thread_id)
    display_title = title[:20] + ("..." if len(title) > 20 else "")

    if st.sidebar.button(display_title, key=thread_id):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_message = []
        for mesg in messages:
            if isinstance(mesg, HumanMessage):
                role = 'user'
            elif isinstance(mesg, AIMessage):
                role = 'assistant'
            else:
                continue
            temp_message.append({'role': role, 'content': mesg.content})

        st.session_state['message_history'] = temp_message
        st.rerun()

st.sidebar.caption(f"**Active Thread:** `{st.session_state['thread_id']}`")

# 3. Render current thread conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# 4. Handle user input
user_input = st.chat_input('Type here')

if user_input:
    current_thread = st.session_state['thread_id']

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': current_thread}}

    response = chatbot.invoke(
        {'messages': [HumanMessage(content=user_input)]},
        config=CONFIG
    )

    ai_message = response['messages'][-1].content

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.markdown(ai_message)

    st.rerun()