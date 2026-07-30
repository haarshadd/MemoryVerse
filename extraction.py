"""
Module 2: Intelligent Categorization
Module 3: Relationship Engine (partial — extracts the raw signal;
          graph_utils.py turns it into an actual graph)

Single call to a local Ollama model that returns structured JSON:
category, title, date, skills, entities, summary, related_to.
No API key, no internet needed after the model is pulled.
"""
import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"  # swap to "llama3.2:3b" if your machine has more RAM

CATEGORIES = ["Project", "Skill", "Certification", "Internship", "Achievement", "Academic"]

PROMPT_TEMPLATE = """You are a document classifier for a student's digital identity system.
Read the document text below and respond with ONLY a JSON object (no markdown
fences, no explanation, no preamble) with exactly these fields:

{{
  "category": one of {categories},
  "title": a short human-readable title for this document (max 10 words),
  "date": the most relevant date in YYYY-MM-DD or YYYY-MM format if found, else null,
  "skills": array of specific skill/technology names mentioned (e.g. "Python", "React", "Data Analysis"),
  "entities": array of named entities (organizations, course/cert names, project names),
  "summary": one sentence summarizing what this document is,
  "related_to": array of short strings describing what this document likely connects to
                (e.g. "Python certification could relate to any Python-based project")
}}

Document text:
\"\"\"
{document_text}
\"\"\"

JSON:"""


def extract_metadata(document_text: str, max_chars: int = 4000) -> dict:
    """Send document text to local Ollama model, parse structured JSON back."""
    truncated = document_text[:max_chars]
    prompt = PROMPT_TEMPLATE.format(categories=CATEGORIES, document_text=truncated)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        },
        timeout=120,
    )
    response.raise_for_status()
    raw_output = response.json().get("response", "")

    return _parse_json_safely(raw_output)


def _parse_json_safely(raw_output: str) -> dict:
    """Local models sometimes wrap JSON in markdown fences or add stray text —
    strip that before parsing, and fall back to a safe default on failure."""
    cleaned = raw_output.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    # Grab the first {...} block in case the model added extra commentary.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        data = {}

    # Defensive defaults so the rest of the pipeline never crashes on a bad parse.
    return {
        "category": data.get("category") if data.get("category") in CATEGORIES else "Academic",
        "title": data.get("title", "Untitled document"),
        "date": data.get("date"),
        "skills": data.get("skills", []) or [],
        "entities": data.get("entities", []) or [],
        "summary": data.get("summary", ""),
        "related_to": data.get("related_to", []) or [],
    }
