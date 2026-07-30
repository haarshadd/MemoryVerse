import os
import uuid
import json
import streamlit as st

from ingestion import extract_text
from extraction import extract_metadata, CATEGORIES
from vectorstore import add_document, search, get_all_documents
from graph_utils import build_graph, render_pyvis

UPLOAD_DIR = "data/uploads"
METADATA_DIR = "data/metadata"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

st.set_page_config(page_title="MemoryVerse", page_icon="🧠", layout="wide")
st.title("🧠 MemoryVerse — Your Digital Identity")
st.caption("Upload once. Never search through folders again.")

tab_upload, tab_search, tab_timeline, tab_graph = st.tabs(
    ["📤 Upload", "🔍 Smart Search", "📅 Timeline", "🕸️ Relationship Graph"]
)

# ---------------------------------------------------------------------------
# TAB 1: Upload (Module 1 + 2 + 3 pipeline)
# ---------------------------------------------------------------------------
with tab_upload:
    st.subheader("Upload certificates, resumes, project reports, internship letters...")
    uploaded_files = st.file_uploader(
        "Drop files here",
        accept_multiple_files=True,
        type=["pdf", "docx", "png", "jpg", "jpeg", "txt", "md"],
    )

    if uploaded_files:
        for uf in uploaded_files:
            doc_id = str(uuid.uuid4())
            save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{uf.name}")
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())

            with st.status(f"Processing {uf.name}...", expanded=True) as status:
                st.write("Extracting text...")
                try:
                    text = extract_text(save_path)
                except Exception as e:
                    st.error(f"Could not parse {uf.name}: {e}")
                    continue

                if not text.strip():
                    st.warning("No text found (possibly a scanned file with no OCR available).")
                    text = uf.name  # fall back so it's still searchable by filename

                st.write("Categorizing with local AI model (Ollama)...")
                try:
                    metadata = extract_metadata(text)
                except Exception as e:
                    st.error(
                        f"Could not reach local Ollama model: {e}\n\n"
                        "Make sure `ollama serve` is running and you've pulled the model "
                        "(see README)."
                    )
                    continue

                metadata["file_path"] = save_path
                metadata["original_filename"] = uf.name

                st.write("Storing in vector database...")
                add_document(doc_id, text, metadata)

                with open(os.path.join(METADATA_DIR, f"{doc_id}.json"), "w") as f:
                    json.dump(metadata, f, indent=2)

                status.update(label=f"✅ {uf.name} → {metadata['category']}", state="complete")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {metadata['category']}")
                st.write(f"**Title:** {metadata['title']}")
                st.write(f"**Date:** {metadata.get('date') or 'not detected'}")
            with col2:
                st.write(f"**Skills:** {', '.join(metadata['skills']) or 'none detected'}")
                st.write(f"**Summary:** {metadata.get('summary', '')}")

# ---------------------------------------------------------------------------
# TAB 2: Smart Retrieval (Module 5)
# ---------------------------------------------------------------------------
with tab_search:
    st.subheader("Ask for anything in plain English")
    st.caption('Try: "show my certificates" · "AI projects" · "internship documents" · "latest resume"')

    with st.form("search_form"):
        query = st.text_input("Search", placeholder="Show my AI projects")
        category_filter = st.selectbox("Filter by category (optional)", ["Any"] + CATEGORIES)
        submitted = st.form_submit_button("Search")

    if submitted and query:
        cat = None if category_filter == "Any" else category_filter
        results = search(query, n_results=10, category_filter=cat)

        if not results:
            st.info("No matches yet — upload some documents first.")
        for r in results:
            meta = r["metadata"]
            with st.container(border=True):
                st.write(f"**{meta.get('title')}**  ·  {meta.get('category')}  ·  {meta.get('date') or 'no date'}")
                st.caption(meta.get("summary", ""))
                if meta.get("file_path") and os.path.exists(meta["file_path"]):
                    with open(meta["file_path"], "rb") as f:
                        st.download_button(
                            "⬇ Download original file",
                            f.read(),
                            file_name=os.path.basename(meta["file_path"]),
                            key=r["id"],
                        )

# ---------------------------------------------------------------------------
# TAB 3: Timeline (Module 4)
# ---------------------------------------------------------------------------
with tab_timeline:
    st.subheader("Your growth, chronologically")
    docs = get_all_documents()

    dated_docs = [d for d in docs if d["metadata"].get("date")]
    dated_docs.sort(key=lambda d: d["metadata"]["date"])

    if not dated_docs:
        st.info("Upload documents with detectable dates to build your timeline.")
    for d in dated_docs:
        meta = d["metadata"]
        st.markdown(f"**{meta.get('date')}** → {meta.get('title')}  \n*{meta.get('category')}* — {meta.get('summary', '')}")
        st.divider()

# ---------------------------------------------------------------------------
# TAB 4: Relationship Graph (Module 3 visualized)
# ---------------------------------------------------------------------------
with tab_graph:
    st.subheader("How your certifications, skills, projects & internships connect")
    docs = get_all_documents()

    if len(docs) < 2:
        st.info("Upload at least 2 documents to see connections.")
    else:
        G = build_graph(docs)
        if G.number_of_edges() == 0:
            st.warning("No shared skills detected yet between your documents.")
        html_path = render_pyvis(G)
        with open(html_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=620, scrolling=True)
