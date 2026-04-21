# backend/rag/repo_loader.py
import os
import git
import uuid
import shutil
import chromadb
import streamlit as st
from chromadb.config import Settings
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"

SUPPORTED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx", ".py"]
SKIP_DIRS = {"node_modules", ".git", ".next", "__pycache__", "venv", "dist", "build"}


@st.cache_resource
def get_chroma_client():
    """Cached ChromaDB client — created once per session."""
    return chromadb.PersistentClient(
        path="./chroma_store",
        settings=Settings(anonymized_telemetry=False)
    )


@st.cache_resource
def get_embed_model():
    """
    WHY: sentence-transformers runs locally for free on Streamlit Cloud.
    Replaces Ollama nomic-embed-text — same semantic quality, no local server needed.
    Cached so the model is loaded once, not on every rerun.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list:
    model = get_embed_model()
    return model.encode(text).tolist()


def detect_framework(repo_path: str) -> str:
    pkg = os.path.join(repo_path, "package.json")
    if os.path.exists(pkg):
        with open(pkg, "r") as f:
            c = f.read().lower()
            if "next"    in c: return "nextjs"
            if "react"   in c: return "react"
            if "express" in c: return "express"
            if "nestjs"  in c: return "nestjs"

    req = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(req):
        with open(req, "r") as f:
            c = f.read().lower()
            if "fastapi" in c: return "fastapi"
            if "django"  in c: return "django"

    return "unknown"


def extract_code_chunks(repo_path: str) -> list:
    chunks = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for file in files:
            if os.path.splitext(file)[1] not in SUPPORTED_EXTENSIONS:
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if len(content) < 50:
                    continue
                for i in range(0, len(content), 400):
                    chunk = content[i:i + 500]
                    if len(chunk) > 50:
                        chunks.append({
                            "text": chunk,
                            "file": file_path.replace(repo_path, ""),
                            "ext":  os.path.splitext(file)[1]
                        })
            except Exception:
                continue
    return chunks


def store_embeddings(chunks: list, repo_id: str, progress_callback=None):
    chroma_client = get_chroma_client()
    collection    = chroma_client.get_or_create_collection(f"repo_{repo_id}")

    texts     = [c["text"] for c in chunks]
    ids       = [f"{repo_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"file": c["file"], "ext": c["ext"]} for c in chunks]

    model          = get_embed_model()
    batch_size     = 32
    total          = len(texts)
    all_embeddings = []

    for i in range(0, total, batch_size):
        batch      = texts[i:i + batch_size]
        embeddings = model.encode(batch).tolist()
        all_embeddings.extend(embeddings)
        if progress_callback:
            progress_callback(min(i + batch_size, total), total)

    collection.add(
        documents=texts,
        embeddings=all_embeddings,
        ids=ids,
        metadatas=metadatas
    )


def cleanup_old_repos(keep: int = 5):
    temp_dir = "./temp_repos"
    if not os.path.exists(temp_dir):
        return
    folders = sorted(
        [os.path.join(temp_dir, d) for d in os.listdir(temp_dir)],
        key=os.path.getmtime
    )
    for old in folders[:-keep]:
        try:
            shutil.rmtree(old)
        except Exception:
            pass


def load_repository(github_url: str, progress_callback=None) -> dict:
    """Full ETL pipeline: Clone → Detect → Chunk → Embed → Store"""
    cleanup_old_repos(keep=5)
    repo_id    = str(uuid.uuid4())[:8]
    clone_path = f"./temp_repos/{repo_id}"
    try:
        git.Repo.clone_from(github_url, clone_path)
        framework = detect_framework(clone_path)
        chunks    = extract_code_chunks(clone_path)
        store_embeddings(chunks, repo_id, progress_callback)
        return {
            "success":       True,
            "repo_id":       repo_id,
            "framework":     framework,
            "files_indexed": len(chunks),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
