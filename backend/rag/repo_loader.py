# backend/rag/repo_loader.py
import os
import git
import uuid
import shutil
import requests
import chromadb
import streamlit as st
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

# ── Disable telemetry BEFORE client creation ──────────────────
os.environ["ANONYMIZED_TELEMETRY"] = "False"

OLLAMA_URL  = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

SUPPORTED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx", ".py"]
SKIP_DIRS = {"node_modules", ".git", ".next", "__pycache__", "venv", "dist", "build"}


@st.cache_resource
def get_chroma_client():
    """
    WHY: Cached so the ChromaDB client is created ONCE per session,
    not on every Streamlit rerun. Avoids repeated telemetry calls
    and connection overhead.
    """
    return chromadb.PersistentClient(
        path="./chroma_store",
        settings=Settings(anonymized_telemetry=False)
    )


def get_embedding(text: str) -> list:
    """
    WHY: Local Ollama embedding replaces OpenAI text-embedding-ada-002.
    Zero cost, works offline, same semantic quality for code search.
    """
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["embedding"]


def get_embeddings_batch(texts: list) -> list:
    """
    WHY: Reuses a single requests.Session for all embedding calls
    instead of opening a new connection per chunk — significantly
    faster for large repos with hundreds of chunks.
    """
    embeddings = []
    session = requests.Session()
    for text in texts:
        r = session.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30
        )
        r.raise_for_status()
        embeddings.append(r.json()["embedding"])
    return embeddings


def detect_framework(repo_path: str) -> str:
    """
    WHY: Auto-detect so the agent can inject framework-specific
    conventions into the generation prompt without manual input.
    """
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
    """
    WHY: 500-char windows with 100-char overlap preserves
    function context without losing cross-boundary semantics.
    """
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


def collection_exists(repo_id: str) -> bool:
    """
    WHY: Skip re-indexing if this repo was already embedded in a
    previous session. Saves minutes of embedding time on reload.
    """
    chroma_client = get_chroma_client()
    existing = [c.name for c in chroma_client.list_collections()]
    return f"repo_{repo_id}" in existing


def store_embeddings(chunks: list, repo_id: str, progress_callback=None):
    """
    WHY: ChromaDB persists embeddings — same repo won't need
    re-indexing in future sessions. Uses session-reused HTTP
    connection for faster batch embedding.
    """
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(f"repo_{repo_id}")

    texts     = [c["text"] for c in chunks]
    ids       = [f"{repo_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"file": c["file"], "ext": c["ext"]} for c in chunks]

    # Embed in batches of 10, reusing HTTP session
    all_embeddings = []
    batch_size     = 10
    total          = len(texts)
    session        = requests.Session()

    for i in range(0, total, batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            r = session.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
                timeout=30
            )
            r.raise_for_status()
            all_embeddings.append(r.json()["embedding"])

        if progress_callback:
            progress_callback(min(i + batch_size, total), total)

    collection.add(
        documents=texts,
        embeddings=all_embeddings,
        ids=ids,
        metadatas=metadatas
    )


def cleanup_old_repos(keep: int = 5):
    """
    WHY: temp_repos accumulates cloned folders forever.
    Keep only the N most recent to avoid disk bloat.
    """
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
    """
    Full ETL pipeline: Clone → Detect → Chunk → Embed → Store
    """
    cleanup_old_repos(keep=5)   # remove stale clones first

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