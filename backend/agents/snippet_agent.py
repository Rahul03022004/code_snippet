# backend/agents/snippet_agent.py
import os
import chromadb
import streamlit as st
from chromadb.config import Settings
from groq import Groq
from dotenv import load_dotenv
from backend.validators.ast_validator import validate_syntax

load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"

# NOTE: Models read inside functions so sidebar changes take effect immediately.

FRAMEWORK_TEMPLATES = {
    "nextjs": """You are a Next.js 14 App Router expert.
Rules:
- 'use client' only when using browser APIs or hooks
- Server Components by default (no directive)
- TypeScript with explicit types on all props/returns
- File naming: page.tsx, layout.tsx, route.ts
OUTPUT: raw code only. No markdown. No explanation.""",

    "react": """You are a React 18 expert.
Rules:
- Functional components only
- Custom hooks for reusable logic
- TypeScript interfaces for all props
OUTPUT: raw code only. No markdown. No explanation.""",

    "express": """You are an Express.js backend expert.
Rules:
- async/await with try/catch on every handler
- Proper HTTP status codes
- Separate routes → controllers → services
OUTPUT: raw code only. No markdown. No explanation.""",

    "nestjs": """You are a NestJS expert.
Rules:
- Use @Controller, @Get, @Post, @Injectable decorators
- Dependency injection via constructor
- DTOs with class-validator
OUTPUT: raw code only. No markdown. No explanation.""",

    "fastapi": """You are a FastAPI expert.
Rules:
- Pydantic BaseModel for all schemas
- async def for all endpoints
- Full type hints everywhere
OUTPUT: raw code only. No markdown. No explanation.""",

    "django": """You are a Django expert.
Rules:
- Class-based views where appropriate
- Django ORM for all DB operations
- Serializers for validation
OUTPUT: raw code only. No markdown. No explanation.""",

    "unknown": """You are an expert software developer.
Write clean, production-ready code.
OUTPUT: raw code only. No markdown. No explanation."""
}


@st.cache_resource
def get_chroma_client():
    """Cached ChromaDB client — created once per session."""
    return chromadb.PersistentClient(
        path="./chroma_store",
        settings=Settings(anonymized_telemetry=False)
    )


@st.cache_resource
def get_groq_client():
    """
    WHY: Cached Groq client — created once per session.
    Groq replaces Ollama for cloud deployment: free tier,
    extremely fast inference, no local server required.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Add it to .env or Streamlit secrets.")
    return Groq(api_key=api_key)


def get_embedding(text: str) -> list:
    """Uses the cached sentence-transformer model from repo_loader."""
    from backend.rag.repo_loader import get_embed_model
    model = get_embed_model()
    return model.encode(text).tolist()


def generate_with_groq(system_prompt: str, user_prompt: str) -> str:
    """
    WHY: Groq runs llama3 on their cloud hardware — same model as
    local Ollama but ~10x faster and works on Streamlit Cloud.
    """
    client    = get_groq_client()
    llm_llm_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    response = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()


def retrieve_context(intent: str, repo_id: str) -> str:
    try:
        chroma_client   = get_chroma_client()
        collection      = chroma_client.get_collection(f"repo_{repo_id}")
        query_embedding = get_embedding(intent)
        results         = collection.query(query_embeddings=[query_embedding], n_results=3)

        docs  = results["documents"][0]
        files = [m["file"] for m in results["metadatas"][0]]
        return "\n\n---\n\n".join(f"// From: {f}\n{c}" for f, c in zip(files, docs))

    except Exception as e:
        print(f"[retrieve_context] RAG failed for repo_id={repo_id}: {e}")
        return ""


def check_code_smells(code: str) -> list:
    smells = []
    lines  = code.split('\n')

    if len(lines) > 50:
        smells.append("⚠️ Long Method (>50 lines)")

    unique = set(l.strip() for l in lines if l.strip())
    if len(lines) - len(unique) > 5:
        smells.append("⚠️ Duplicate Code")

    for ind in ["TODO", "FIXME", "console.log", "debugger"]:
        if ind in code:
            smells.append(f"⚠️ Dead Code Indicator: `{ind}`")

    if code.count("def ") > 20 or code.count("function ") > 20:
        smells.append("⚠️ God Class (too many methods)")

    return smells


def score_snippet(snippet: str, smells: list, has_context: bool, is_valid: bool) -> dict:
    scores = {
        "Syntax Valid":    25 if is_valid else 0,
        "Smell Free":      max(0, 25 - len(smells) * 5),
        "Context Aligned": 25 if has_context else 15,
        "Completeness":    0,
    }
    has_todos   = "TODO" in snippet or "placeholder" in snippet.lower()
    good_length = 10 < len(snippet.split('\n')) < 60
    scores["Completeness"] = 25 if (not has_todos and good_length) else 15 if good_length else 10
    scores["total"]        = sum(v for k, v in scores.items() if k != "total")
    return scores


def clean_output(text: str) -> str:
    lines = text.split('\n')
    return '\n'.join(l for l in lines if not l.strip().startswith("```")).strip()


def generate_smell_fix(snippet: str, smells: list) -> str:
    if not smells:
        return None
    return generate_with_groq(
        system_prompt="You are a refactoring expert. Fix ONLY the listed smells. Keep logic identical. Raw code only.",
        user_prompt=f"Smells: {', '.join(smells)}\n\nCode:\n{snippet}\n\nRefactored:"
    )


def generate_snippet(intent: str, framework: str, repo_id: str, log=None) -> dict:
    def _log(msg):
        if log: log(msg)

    _log("🔍 Step 1/5 — Retrieving codebase context via RAG...")
    context     = retrieve_context(intent, repo_id)
    has_context = len(context) > 0
    _log(f"   Context found: {'✅ Yes' if has_context else '⚠️ No (using best practices)'}")

    _log("📝 Step 2/5 — Building framework-aware prompt...")
    fw_instruction = FRAMEWORK_TEMPLATES.get(framework, FRAMEWORK_TEMPLATES["unknown"])
    system_prompt  = f"""{fw_instruction}
Additional rules:
- Match the coding style from the context snippets
- Functions under 40 lines
- No duplicate logic
- No TODO or placeholder comments
- Fully working production-ready code"""

    user_prompt = (
        f"Developer intent: {intent}\n\n"
        f"Existing codebase patterns to match:\n"
        f"{context if has_context else 'No context — use framework best practices'}\n\n"
        f"Generate the code snippet:"
    )

    llm_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    _log(f"🧠 Step 3/5 — Generating with Groq ({llm_model})...")
    max_retries = 3
    snippet     = ""
    is_valid    = False

    for attempt in range(max_retries):
        raw     = generate_with_groq(system_prompt, user_prompt)
        snippet = clean_output(raw)

        _log(f"✅ Step 4/5 — AST validation (attempt {attempt+1}/{max_retries})...")
        is_valid, error = validate_syntax(snippet, framework)

        if is_valid:
            _log("   Syntax: ✅ Valid")
            break
        else:
            _log(f"   Syntax: ❌ {error} — retrying...")
            user_prompt += f"\n\nPrevious attempt had this error: {error}\nFix and regenerate:"

    _log("🔎 Step 5/5 — Checking for code smells...")
    smells = check_code_smells(snippet)
    _log(f"   Smells: {smells if smells else '✅ None'}")

    score = score_snippet(snippet, smells, has_context, is_valid)
    _log(f"📊 Quality Score: {score['total']}/100")

    return {
        "success":         True,
        "snippet":         snippet,
        "framework":       framework,
        "quality_score":   score,
        "smells_detected": smells,
        "syntax_valid":    is_valid,
        "context_used":    has_context,
        "smell_fix":       generate_smell_fix(snippet, smells) if smells else None,
    }
