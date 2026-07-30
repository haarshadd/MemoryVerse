# MemoryVerse — AI-Powered Digital Identity System

Turns a scattered pile of certificates, resumes, project reports, and internship
letters into a searchable, connected, chronological "digital identity" —
fully local, no API keys, no paid services.


Every module in the hackathon brief maps to one piece here:
- **Module 1 (Ingestion)** → `ingestion.py`
- **Module 2 (Categorization)** → the LLM extraction step (`extraction.py`)
- **Module 3 (Relationship Engine)** → `graph_utils.py` (built from the LLM's
  `related_to` output + shared-skill edges)
- **Module 4 (Timeline)** → sort-by-date in `app.py`
- **Module 5 (Smart Retrieval)** → `vectorstore.py` semantic search + original
  file always kept in `data/uploads/`

## Setup

### 1. Install Ollama (the local LLM runtime)

**Windows / Mac:**
Download and run the installer from https://ollama.com/download

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify it's installed:
```bash
ollama --version
```

### 2. Pull the model (one-time, ~1GB download)

```bash
ollama pull qwen2.5:1.5b
```

This model was picked because it's small enough to run comfortably on 8GB RAM
machines while still being solid at structured JSON extraction. If your
machine has more headroom later, `llama3.2:3b` gives noticeably better
extraction quality — just `ollama pull llama3.2:3b` and change `MODEL_NAME`
in `extraction.py`.

### 3. Start Ollama (it usually auto-starts as a background service; if not:)

```bash
ollama serve
```

Leave this running in a terminal. It serves the local API at
`http://localhost:11434`.

### 4. Install Python dependencies

```bash
cd memoryverse
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**OCR note**: for scanned certificate images, `pytesseract` needs the
Tesseract binary installed separately:
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`
- Windows: installer at https://github.com/UB-Mannheim/tesseract/wiki

If you skip this, everything still works for PDFs/docx — just scanned image
certs won't OCR.

### 5. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Demo flow (for judges)

1. Upload 5-10 sample files (a resume, a certificate PDF, a project report,
   an internship letter) — watch each get auto-categorized live.
2. Type a natural query: "show my AI projects" or "show my certificates" —
   instant semantic retrieval, original file downloadable.
3. Open the Timeline tab — chronological growth story.
4. Open the Graph tab — visually click through
   Certification → Skill → Project → Internship links.


## Project structure

```
memoryverse/
├── app.py                # Streamlit UI (entry point)
├── ingestion.py           # File parsing (pdf/docx/image OCR)
├── extraction.py          # Ollama call: categorize + extract entities
├── vectorstore.py         # ChromaDB wrapper: embed, store, semantic search
├── graph_utils.py         # NetworkX relationship graph + pyvis rendering
├── requirements.txt
├── data/
│   ├── uploads/           # original files, always preserved
│   ├── chroma_db/         # vector store (auto-created)
│   └── metadata/          # per-document extracted JSON (auto-created)
└── README.md
```

## How it works (architecture)

<img width="1200" height="1080" alt="architecture_diagram" src="https://github.com/user-attachments/assets/fd249cc7-eed9-47fe-b926-9cfc5d31b904" />

