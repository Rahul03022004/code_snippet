# ⚡ Code Snippet Agent — Streamlit Edition
> Context-aware code generation · RAG · AST Validation · Smell Detection
> Powered by **Ollama llama3.1** — 100% free, runs locally, no API key needed

---

## 🏗️ Project Structure

```
code-snippet-agent-streamlit/
├── app.py                          ← Streamlit UI (single file, run this)
├── .env                            ← Ollama config
├── requirements.txt                ← Python packages
└── backend/
    ├── __init__.py
    ├── agents/
    │   ├── __init__.py
    │   └── snippet_agent.py        ← 6-step agent pipeline
    ├── rag/
    │   ├── __init__.py
    │   └── repo_loader.py          ← Clone → chunk → embed → store
    └── validators/
        ├── __init__.py
        └── ast_validator.py        ← Syntax validation
```

---

## ⚡ Setup (One Time)

### 1. Install Ollama
Download → https://ollama.com/download → Install

### 2. Pull Models
```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 3. Install Python packages
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Run (Every Time)

**Terminal 1 — Start Ollama:**
```bash
ollama serve
```

**Terminal 2 — Start App:**
```bash
venv\Scripts\activate
streamlit run app.py
```

Opens automatically at **http://localhost:8501**

---

## 🧪 How to Use

1. **Load Repo** — Paste any public GitHub URL, click Load
2. **Describe Intent** — Type what you want in plain English
3. **Generate** — Agent runs the full pipeline
4. **Review** — See quality score, smells, auto-fix, download

---

## 🧠 Agent Pipeline (6 Steps)

```
User Intent
    ↓
[1] RAG Retriever      → finds similar code in your repo (ChromaDB)
    ↓
[2] Prompt Builder     → injects framework conventions
    ↓
[3] Ollama Generate    → llama3.1 produces snippet
    ↓
[4] AST Validator      → syntax check, retries up to 3x
    ↓
[5] Smell Detector     → checks output for code smells
    ↓
[6] Quality Scorer     → 4-axis score out of 100
    ↓
Output + Optional Auto-Fix
```

---

## 📊 Quality Score

| Axis | Max | What it checks |
|---|---|---|
| Syntax Valid | 25 | AST parsed without errors |
| Smell Free | 25 | No long methods, duplicates, dead code |
| Context Aligned | 25 | RAG context was available and used |
| Completeness | 25 | No TODOs, appropriate length |

---

## 💡 Tips

- Use a **small repo** (< 500 files) for faster indexing
- If generation is slow, switch to `llama3.2:1b` in the sidebar
- The sidebar shows the last 5 generations for reference
- Click **Download Snippet** to save the code to a file
