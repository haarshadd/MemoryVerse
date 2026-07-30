"""
Module 3: Relationship Engine
Builds a graph connecting documents through shared skills/entities and the
LLM's own "related_to" hints. Two documents are linked if:
  - they share at least one extracted skill, OR
  - they share an entity (e.g. same organization/project name), OR
  - their categories form a known meaningful pair (Certification->Project etc.)
"""
import networkx as nx
from pyvis.network import Network

CATEGORY_COLORS = {
    "Project": "#4C9AFF",
    "Skill": "#57D9A3",
    "Certification": "#FFAB00",
    "Internship": "#FF7452",
    "Achievement": "#998DD9",
    "Academic": "#79E2F2",
}


def build_graph(documents: list[dict]) -> nx.Graph:
    """documents: list of {"id", "metadata": {...}} from vectorstore.get_all_documents()"""
    G = nx.Graph()

    for doc in documents:
        meta = doc["metadata"]
        G.add_node(
            doc["id"],
            label=meta.get("title", doc["id"]),
            category=meta.get("category", "Academic"),
            date=meta.get("date", ""),
            skills=meta.get("skills", ""),
        )

    # Connect documents that share a skill
    for i, doc_a in enumerate(documents):
        skills_a = set(s.strip().lower() for s in doc_a["metadata"].get("skills", "").split(",") if s.strip())
        for doc_b in documents[i + 1:]:
            skills_b = set(s.strip().lower() for s in doc_b["metadata"].get("skills", "").split(",") if s.strip())
            shared = skills_a & skills_b
            if shared:
                G.add_edge(
                    doc_a["id"], doc_b["id"],
                    label=", ".join(list(shared)[:3]),
                    weight=len(shared),
                )

    return G


def render_pyvis(G: nx.Graph, output_path: str = "data/graph.html"):
    """Renders an interactive HTML graph for embedding in Streamlit."""
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#222")
    net.barnes_hut()

    for node_id, attrs in G.nodes(data=True):
        color = CATEGORY_COLORS.get(attrs.get("category"), "#cccccc")
        title = f"{attrs.get('category')} | {attrs.get('date') or 'no date'}\nSkills: {attrs.get('skills')}"
        net.add_node(node_id, label=attrs.get("label", node_id), color=color, title=title)

    for source, target, attrs in G.edges(data=True):
        net.add_edge(source, target, title=attrs.get("label", ""), value=attrs.get("weight", 1))

    net.save_graph(output_path)
    return output_path
