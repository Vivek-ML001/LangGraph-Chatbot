#  LangGraph Chatbot with Streamlit Frontend

An interactive, multi-threaded conversational AI application built with **LangGraph**, **LangChain**, and **Streamlit**. It uses an SQLite checkpointer to persist conversation histories across sessions and dynamically names past threads in the sidebar using actual user prompts, much like ChatGPT and Gemini.

##  Demo
Live: https://chatbot247.streamlit.app/

##  System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                 Streamlit Web UI                        │
│               (streamlit_frontend.py)                   │
└───────────────────────────┬─────────────────────────────┘
                            │
               Invoke Agent │ State Management
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Backend                    │
│                (langgraph_backend.py)                   │
├─────────────────────────────────────────────────────────┤
│  ChatState ──► Chat Node (Groq LLM) ──► Checkpointer    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 SQLite Checkpointer                     │
│                     (chatbot.db)                        │
└─────────────────────────────────────────────────────────┘
```

##  Features

- **Multi-Threaded Conversations:** Create new chats or switch between past sessions using unique `thread_id`s.
- **Persistent State Memory:** All message histories are stored in a local SQLite database (`chatbot.db`) via `SqliteSaver`.
- **Dynamic Sidebar Titles:** The first user prompt of each thread is used as its title instead of a raw UUID.
- **Markdown Support:** Code snippets, tables, lists and rich text render in both user and assistant bubbles.
- **State Recovery:** History survives browser refreshes, restored from the SQLite checkpointer.

##  Project Structure

```text
Lang_Graph_Chat/
├── assets/                  # Screenshots & demo GIF
│   └── demo.gif
├── .env                     # Environment variables (API keys)
├── .gitignore               # Excluded files
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── chatbot.db               # SQLite checkpoints (auto-generated)
├── langgraph_backend.py     # LangGraph state graph & checkpointer setup
└── streamlit_frontend.py    # Streamlit multi-thread UI
```

##  Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Orchestration | LangGraph, LangChain Core |
| LLM Provider | ChatGroq |
| Persistence | `langgraph.checkpoint.sqlite.SqliteSaver` |

##  Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/Vivek-ML001/Lang_Graph_Chat.git
cd Lang_Graph_Chat
```

### 3. Virtual Environment
```bash
python -m venv myenv

# Windows (PowerShell)
.\myenv\Scripts\Activate.ps1

# Mac/Linux
source myenv/bin/activate
```

### 4. Install Dependencies
```bash
pip install streamlit langgraph langchain-core langchain-groq langgraph-checkpoint-sqlite python-dotenv
```

### 5. Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

##  Run the Application
```bash
streamlit run streamlit_frontend.py
```
