import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_backend import chatbot, retrive_all_thread, delete_thread_from_db

# --- Helper Functions ---
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def get_thread_title(thread_id):
    # Check if a custom title exists first
    if thread_id in st.session_state.get('custom_titles', {}):
        return st.session_state['custom_titles'][thread_id]
    
    # Fall back to the first human message
    messages = load_conversation(thread_id)
    for mesg in messages:
        if isinstance(mesg, HumanMessage):
            return mesg.content
    return f"Thread {thread_id[:6]}"

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

# --- 1. Session State Setup ---
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrive_all_thread()

if 'custom_titles' not in st.session_state:
    st.session_state['custom_titles'] = {}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if not st.session_state['chat_thread']:
    new_id = generate_thread_id()
    st.session_state['thread_id'] = new_id
    add_thread(new_id)

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = st.session_state['chat_thread'][0]

# --- 2. Sidebar Setup ---
st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('➕ New Chat', use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.header('My Conversations')

# Render past threads with Delete & Rename actions
for thread_id in st.session_state['chat_thread']:
    title = get_thread_title(thread_id)
    display_title = title[:18] + ("..." if len(title) > 18 else "")

    # Create 3 columns: [Thread Select Button] [Rename Popover] [Delete Button]
    col1, col2, col3 = st.sidebar.columns([0.65, 0.175, 0.175])

    # 1. Switch Active Thread
    with col1:
        # Highlight active thread button visually
        btn_type = "primary" if thread_id == st.session_state['thread_id'] else "secondary"
        if st.button(display_title, key=f"btn_{thread_id}", type=btn_type, use_container_width=True):
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

    # 2. Rename Thread (using st.popover)
    with col2:
        with st.popover("✏️"):
            new_title = st.text_input("New Name", value=title, key=f"input_{thread_id}")
            if st.button("Save", key=f"save_{thread_id}"):
                if new_title.strip():
                    st.session_state['custom_titles'][thread_id] = new_title.strip()
                    st.rerun()

    # 3. Delete Thread
    with col3:
        if st.button("🗑️", key=f"del_{thread_id}"):
            # Delete from DB and session state
            delete_thread_from_db(thread_id)
            st.session_state['chat_thread'].remove(thread_id)
            if thread_id in st.session_state['custom_titles']:
                del st.session_state['custom_titles'][thread_id]

            # If active thread was deleted, reset or switch to another
            if st.session_state['thread_id'] == thread_id:
                if st.session_state['chat_thread']:
                    st.session_state['thread_id'] = st.session_state['chat_thread'][0]
                    messages = load_conversation(st.session_state['thread_id'])
                    st.session_state['message_history'] = [
                        {'role': 'user' if isinstance(m, HumanMessage) else 'assistant', 'content': m.content}
                        for m in messages if isinstance(m, (HumanMessage, AIMessage))
                    ]
                else:
                    reset_chat()

            st.rerun()

st.sidebar.caption(f"**Active Thread:** `{st.session_state['thread_id']}`")

# --- 3. Render Messages & Chat Input ---
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

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
