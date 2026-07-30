# MemoryVerse — Thought Process

## The problem, restated honestly

The brief describes a real annoyance: a student's proof of who they are is scattered across a decade of folders, emails, and drives. But "build a system to organize files" is a problem with a hundred submissions that look the same — upload, tag, search. The interesting question isn't *can we categorize a PDF*. It's: **what would it take for a pile of documents to actually answer a question about a person?**

That reframing is what shaped every decision below.

## Decision 1: local-only, and why that's not just a budget constraint

I built this with zero paid APIs — Ollama running a small model locally, ChromaDB for vectors, everything on-device. That started as a practical constraint (no API keys), but it turned into the right call for the problem itself.

Think about what's actually being uploaded here: certificates with full names, internship letters with company details, resumes with contact information. This is exactly the kind of personal document trail that shouldn't need to leave a laptop to be understood. A "digital identity system" that ships your identity documents to a third-party API to categorize them is a strange thing to build a hackathon prize around. Local-first isn't a workaround — it's the more honest architecture for what this system actually holds.

## Decision 2: one LLM call does three jobs

The brief lists Categorization and Relationship Engine as separate modules. We treat them as one prompt. When a document's text goes to the local model, it comes back with category, extracted skills, entities, a date, and a set of relationship hints — all in one structured JSON response. Splitting this into multiple calls would mean multiple round-trips through a CPU-bound local model, which is the resource you can least afford to spend twice. One well-designed prompt beats three narrow ones.

## Decision 3: retrieval isn't the finish line

This is the actual center of the project. Early on, "smart retrieval" meant: type a query, get back matching files. That's a working feature — but it's also just search with extra steps, and it undersells what the underlying data actually supports.

Once every document has been embedded and tagged with skills, dates, and categories, the system has enough structure to do something a folder never could: **answer a question about the person, not just return documents that match it.** Ask "what am I good at?" and instead of a list of five files, the system retrieves the relevant documents, feeds them to the local model as context, and returns a synthesized answer — a sentence or two, grounded in what was actually uploaded, with each claim traceable back to its source file.

This is the feature we'd want you to remember. It's the difference between a system that stores a journey and one that can actually talk about it.

## What I chose not to build, and why

- **No cloud vector DB, no hosted LLM** — see Decision 1.
- **No custom graph database** — a full graph DB is real infrastructure for a demo that needs to run on a laptop in a few minutes. NetworkX in memory, rebuilt from the extracted metadata each time, does the same conceptual job (Certification → Skill → Project → Internship) without the operational weight.
- **No manual tagging fallback** — the brief's core question is whether the system can organize *without* manual sorting. Adding a manual override path would have quietly answered "no" to the question the challenge is actually asking.

## Where this could go next

The natural extension is longitudinal: right now the system understands a snapshot of uploaded documents. The more interesting version tracks how someone's skill graph *changes* over time — which certifications preceded which projects, which projects preceded which internships — and can answer not just "what am I good at" but "how did I get here." That's a bigger scope than a hackathon weekend, but it's the direction the "digital identity" framing points toward if taken seriously.

## Honest tradeoffs

Running everything locally on modest hardware means slower processing than a cloud API would give — seconds per document rather than instant. For a demo with a handful of curated files, that's a fair trade for zero cost and zero data leaving the machine. It would not yet be the right tradeoff at real scale, and that's a fair question for a judge to raise.
