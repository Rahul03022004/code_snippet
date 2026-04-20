import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama

# -------------------------------
# 🚀 Page Config
# -------------------------------
st.set_page_config(page_title="C++ RAG Chatbot", layout="wide")
st.title("💭 C++ RAG Chatbot")

st.markdown("Ask questions about **C++** and get answers based on your documentation.")

# -------------------------------
# 🔐 Load Environment
# -------------------------------
load_dotenv()

# -------------------------------
# 📦 Load & Cache Vector Store
# -------------------------------
@st.cache_resource
def load_vectorstore():
    loader = TextLoader("C++_Introduction.txt", encoding="utf-8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )

    docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(docs, embeddings)
    return db

db = load_vectorstore()

# -------------------------------
# 🤖 Load Ollama Model
# -------------------------------
llm = Ollama(model="gemma2:2b")

# -------------------------------
# 💬 Chat Memory
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# 💬 Chat Input
# -------------------------------
user_input = st.chat_input("Ask a question about C++...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("🔍 Searching documentation..."):
        docs = db.similarity_search(user_input, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a C++ expert assistant.
Answer the question clearly using ONLY the provided context.

Context:
{context}

Question:
{user_input}

Answer:
"""

    with st.spinner("🤖 Generating answer..."):
        response = llm.invoke(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

# -------------------------------
# 💬 Display Chat
# -------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Assistant:** {msg['content']}")