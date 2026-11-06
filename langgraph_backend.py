import os
import sqlite3
import tempfile
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import sqlite3
import tempfile

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


DB_PATH = os.path.join(tempfile.gettempdir(), "chatbot.db")
conn = sqlite3.connect(database=DB_PATH, check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)           

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrive_all_thread():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread)   



# CONFIG = {'configurable': {'thread_id': 'thread-1'}}



# response = chatbot.invoke(
#     {
#         'messages': [
#             HumanMessage(content='hey my name is vivek')
#         ]
#     },
#     config= CONFIG
# )

# chatbot.get_state(config =CONFIG).value['message']

