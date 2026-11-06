import sqlite3
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# State Definition
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# 1. Connect to SQLite with thread safety & lock timeout
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False, timeout=10)

# 2. Setup Checkpointer
checkpointer = SqliteSaver(conn=conn)
checkpointer.setup()  # Prevents runtime table lock crashes

# 3. Build & Compile LangGraph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# 4. Safely Retrieve All Thread IDs
def retrive_all_thread():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        return [row[0] for row in rows if row[0]]
    except Exception as e:
        print(f"Error fetching thread IDs: {e}")
        return []

# 5. Complete Thread Deletion Helper
def delete_thread_from_db(thread_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM checkpoint_blobs WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM checkpoint_writes WHERE thread_id = ?", (thread_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting thread {thread_id}: {e}")
