import os
import streamlit as st
from dotenv import load_dotenv

# Langchain imports
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# -------------------------------
# 🚀 Page Config
# -------------------------------
st.set_page_config(
    page_title="C++ RAG Chatbot",
    page_icon="💭",
    layout="wide"
)

# -------------------------------
# 🌈 Animated + Premium UI
# -------------------------------
st.markdown("""
<style>

/* 🌈 Animated Gradient Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c1f26);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* ✨ Glowing Title */
h1 {
    text-align: center;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px #00f2ff; }
    to { text-shadow: 0 0 25px #00f2ff, 0 0 40px #0077ff; }
}

/* 🌟 Highlighted Tagline */
.highlight-text {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    padding: 12px 20px;
    margin-top: -10px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    display: inline-block;
    animation: fadeInTagline 1.2s ease;
}

.gradient-text {
    background: linear-gradient(90deg, #00f2ff, #4facfe, #00f2ff);
    background-size: 200% auto;
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    to { background-position: 200% center; }
}

@keyframes fadeInTagline {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 💬 Chat Container */
.chat-container {
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
}

/* 👤 User Bubble */
.user-message {
    background: linear-gradient(135deg, #2962FF, #00C6FF);
    padding: 12px 16px;
    border-radius: 20px;
    color: white;
    margin-bottom: 10px;
    animation: fadeInUp 0.6s ease;
}

/* 🤖 Bot Bubble */
.bot-message {
    background: linear-gradient(135deg, #00b09b, #96c93d);
    padding: 12px 16px;
    border-radius: 20px;
    color: white;
    margin-bottom: 10px;
    animation: fadeInUp 0.8s ease;
}

/* 📦 Chunk Cards */
.chunk-card {
    background: rgba(255,255,255,0.08);
    padding:18px;
    margin-top:15px;
    border-radius:15px;
    border: 1px solid rgba(0,242,255,0.4);
    backdrop-filter: blur(10px);
    animation: fadeInUp 0.6s ease;
}

.chunk-title {
    color:#00f2ff;
    font-weight:600;
}

.chunk-text {
    color:white;
    font-size:15px;
    line-height:1.6;
}

/* 🎬 Fade Animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ⌨ Typing Animation */
.typing {
    display: inline-block;
    overflow: hidden;
    border-right: .15em solid white;
    white-space: nowrap;
    animation: typing 2s steps(30, end), blink .75s step-end infinite;
}

@keyframes typing {
    from { width: 0 }
    to { width: 100% }
}

@keyframes blink {
    from, to { border-color: transparent }
    50% { border-color: white }
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧠 Header
# -------------------------------
st.title("💭 C++ RAG Chatbot")

st.markdown("""
<div style="text-align:center;">
    <div class="highlight-text">
        <span class="gradient-text">
            Ask questions about C++ and get answers based on your documentation.
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 🔐 Load Env
# -------------------------------
load_dotenv()

# -------------------------------
# 📦 Load & Cache Vector Store
# -------------------------------
@st.cache_resource
def load_vector_store():
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

db = load_vector_store()

# -------------------------------
# 💬 Chat Input
# -------------------------------
query = st.text_input("💬 Ask a question about C++:")

if query:
    with st.spinner("🔍 Searching relevant documentation..."):
        relevant_docs = db.similarity_search(query, k=3)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # User message
    st.markdown(
        f'<div class="user-message">🧑‍💻 {query}</div>',
        unsafe_allow_html=True
    )

    # Bot typing animation
    st.markdown(
        '<div class="bot-message"><span class="typing">🤖 Searching knowledge base...</span></div>',
        unsafe_allow_html=True
    )

    # Highlighted chunk cards
    for i, doc in enumerate(relevant_docs):
        st.markdown(f"""
        <div class="chunk-card">
            <div class="chunk-title">📄 Source Chunk {i+1}</div>
            <div class="chunk-text">{doc.page_content}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
