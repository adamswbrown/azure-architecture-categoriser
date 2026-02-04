"""Documentation page - Browse and read project documentation."""

import sys
from pathlib import Path

import streamlit as st

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Documentation metadata for nice display
DOC_METADATA = {
    "architecture-scorer.md": {
        "title": "Architecture Scorer",
        "icon": "🎯",
        "description": "The scoring engine that evaluates applications against architecture patterns",
        "category": "Core Components",
    },
    "recommendations-app.md": {
        "title": "Recommendations App",
        "icon": "🖥️",
        "description": "Customer-facing web application for getting architecture recommendations",
        "category": "Core Components",
    },
    "catalog-builder.md": {
        "title": "Catalog Builder",
        "icon": "📚",
        "description": "Tool for building architecture catalogs from Azure Architecture Center",
        "category": "Core Components",
    },
    "configuration.md": {
        "title": "Configuration Guide",
        "icon": "⚙️",
        "description": "Complete reference for all configuration options and scoring weights",
        "category": "Configuration",
    },
    "drmigrate-integration.md": {
        "title": "Dr. Migrate Integration",
        "icon": "🔄",
        "description": "How to get recommendations for all applications using Dr. Migrate data",
        "category": "Integrations",
    },
    "azure-deployment.md": {
        "title": "Azure Deployment",
        "icon": "☁️",
        "description": "Deploy the application to Azure Container Apps",
        "category": "Deployment",
    },
    "architecture-categorization-guide.md": {
        "title": "Architecture Categorization",
        "icon": "🏷️",
        "description": "How architectures are classified and categorized",
        "category": "Reference",
    },
    "reviewing-the-catalog.md": {
        "title": "Reviewing the Catalog",
        "icon": "🔍",
        "description": "Guide to reviewing and understanding the architecture catalog",
        "category": "Reference",
    },
    "catalog-comparison.md": {
        "title": "Catalog Comparison",
        "icon": "📊",
        "description": "Compare different catalog configurations and their results",
        "category": "Reference",
    },
    "securityaudit.md": {
        "title": "Security Audit",
        "icon": "🔒",
        "description": "Security measures and audit results for the application",
        "category": "Security",
    },
}

# Category order for display
CATEGORY_ORDER = [
    "Core Components",
    "Configuration",
    "Integrations",
    "Deployment",
    "Reference",
    "Security",
]


def get_docs_directory() -> Path | None:
    """Find the docs directory."""
    # Try relative to this file
    docs_dir = Path(__file__).parent.parent.parent.parent / "docs"
    if docs_dir.exists():
        return docs_dir

    # Try relative to cwd
    docs_dir = Path.cwd() / "docs"
    if docs_dir.exists():
        return docs_dir

    # Try /app (Docker)
    docs_dir = Path("/app/docs")
    if docs_dir.exists():
        return docs_dir

    return None


def load_doc_content(docs_dir: Path, filename: str) -> str | None:
    """Load a documentation file's content."""
    try:
        doc_path = docs_dir / filename
        if doc_path.exists():
            return doc_path.read_text(encoding="utf-8")
    except Exception:
        pass
    return None


def get_available_docs(docs_dir: Path) -> list[dict]:
    """Get list of available documentation files with metadata."""
    docs = []

    for md_file in sorted(docs_dir.glob("*.md")):
        filename = md_file.name

        # Skip design docs and internal files
        if filename.startswith("_") or "/design/" in str(md_file):
            continue

        # Get metadata or create default
        metadata = DOC_METADATA.get(filename, {
            "title": filename.replace(".md", "").replace("-", " ").title(),
            "icon": "📄",
            "description": "",
            "category": "Other",
        })

        docs.append({
            "filename": filename,
            "path": md_file,
            **metadata,
        })

    return docs


def render_sidebar_footer() -> None:
    """Render the sidebar footer with credits and links."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 1rem 0; color: #666; font-size: 0.85rem;">
            <p style="margin-bottom: 0.5rem;">
                Built by <a href="https://askadam.cloud/#about" target="_blank"><strong>Adam Brown</strong></a><br/>
                with help from Claude & Copilot
            </p>
            <a href="https://github.com/adamswbrown/azure-architecture-categoriser" target="_blank">
                <img src="https://img.shields.io/badge/View_on-GitHub-181717?style=for-the-badge&logo=github" alt="View on GitHub"/>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_doc_card(doc: dict, is_selected: bool = False) -> bool:
    """Render a documentation card. Returns True if clicked."""
    border_color = "#0078D4" if is_selected else "#e0e0e0"
    bg_color = "#f0f7ff" if is_selected else "#ffffff"

    with st.container():
        clicked = st.button(
            f"{doc['icon']} {doc['title']}",
            key=f"doc_{doc['filename']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        )
        if doc.get("description"):
            st.caption(doc["description"])

    return clicked


def render_table_of_contents(content: str) -> None:
    """Extract and render a table of contents from markdown headings."""
    lines = content.split("\n")
    toc_items = []

    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip()
            anchor = heading.lower().replace(" ", "-").replace(".", "").replace("(", "").replace(")", "")
            toc_items.append({"level": 2, "text": heading, "anchor": anchor})
        elif line.startswith("### "):
            heading = line[4:].strip()
            anchor = heading.lower().replace(" ", "-").replace(".", "").replace("(", "").replace(")", "")
            toc_items.append({"level": 3, "text": heading, "anchor": anchor})

    if toc_items:
        with st.expander("📑 Table of Contents", expanded=False):
            for item in toc_items:
                indent = "  " if item["level"] == 3 else ""
                st.markdown(f"{indent}- {item['text']}")


def main():
    st.set_page_config(
        page_title="Documentation - Azure Architecture Recommendations",
        page_icon="📖",
        layout="wide",
    )

    # Custom CSS for better documentation display
    st.markdown("""
    <style>
    /* Sticky sidebar navigation */
    [data-testid="column"]:first-child {
        position: sticky;
        top: 0;
        height: 100vh;
        overflow-y: auto;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    /* Style the scrollbar for sidebar */
    [data-testid="column"]:first-child::-webkit-scrollbar {
        width: 6px;
    }

    [data-testid="column"]:first-child::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }

    [data-testid="column"]:first-child::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }

    [data-testid="column"]:first-child::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }

    /* Documentation content styling */
    .doc-content {
        max-width: 900px;
        line-height: 1.7;
    }

    .doc-content h1 {
        color: #0078D4;
        border-bottom: 2px solid #0078D4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }

    .doc-content h2 {
        color: #333;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
    }

    .doc-content h3 {
        color: #444;
        margin-top: 1.2rem;
    }

    .doc-content code {
        background: #f5f5f5;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
    }

    .doc-content pre {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
    }

    .doc-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }

    .doc-content th, .doc-content td {
        border: 1px solid #e0e0e0;
        padding: 0.5rem 1rem;
        text-align: left;
    }

    .doc-content th {
        background: #f5f5f5;
        font-weight: 600;
    }

    .doc-content blockquote {
        border-left: 4px solid #0078D4;
        margin: 1rem 0;
        padding: 0.5rem 1rem;
        background: #f0f7ff;
        color: #333;
    }

    /* Category header styling */
    .category-header {
        color: #666;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #e0e0e0;
    }

    /* Sidebar doc list styling */
    .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render sidebar footer
    render_sidebar_footer()

    # Get docs directory
    docs_dir = get_docs_directory()

    if not docs_dir:
        st.error("Documentation directory not found.")
        st.info("The docs/ folder should be in the project root.")
        return

    # Get available docs
    available_docs = get_available_docs(docs_dir)

    if not available_docs:
        st.warning("No documentation files found.")
        return

    # Create two-column layout
    sidebar_col, content_col = st.columns([1, 3])

    with sidebar_col:
        st.markdown("## 📖 Documentation")
        st.caption("Browse project documentation")

        # Search
        search_term = st.text_input(
            "Search docs",
            placeholder="Search...",
            label_visibility="collapsed"
        )

        # Filter docs by search
        if search_term:
            filtered_docs = [
                d for d in available_docs
                if search_term.lower() in d["title"].lower()
                or search_term.lower() in d.get("description", "").lower()
            ]
        else:
            filtered_docs = available_docs

        # Get or set selected doc
        if "selected_doc" not in st.session_state:
            st.session_state.selected_doc = filtered_docs[0]["filename"] if filtered_docs else None

        # Group docs by category
        docs_by_category: dict[str, list] = {}
        for doc in filtered_docs:
            category = doc.get("category", "Other")
            if category not in docs_by_category:
                docs_by_category[category] = []
            docs_by_category[category].append(doc)

        # Render docs grouped by category
        for category in CATEGORY_ORDER:
            if category in docs_by_category:
                st.markdown(f'<div class="category-header">{category}</div>', unsafe_allow_html=True)

                for doc in docs_by_category[category]:
                    is_selected = st.session_state.selected_doc == doc["filename"]

                    if st.button(
                        f"{doc['icon']} {doc['title']}",
                        key=f"btn_{doc['filename']}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                    ):
                        st.session_state.selected_doc = doc["filename"]
                        st.rerun()

        # Handle "Other" category
        if "Other" in docs_by_category:
            st.markdown('<div class="category-header">Other</div>', unsafe_allow_html=True)
            for doc in docs_by_category["Other"]:
                is_selected = st.session_state.selected_doc == doc["filename"]
                if st.button(
                    f"{doc['icon']} {doc['title']}",
                    key=f"btn_{doc['filename']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    st.session_state.selected_doc = doc["filename"]
                    st.rerun()

    with content_col:
        # Load and display selected doc
        selected_filename = st.session_state.selected_doc

        if selected_filename:
            # Find the doc metadata
            doc_meta = next(
                (d for d in available_docs if d["filename"] == selected_filename),
                None
            )

            if doc_meta:
                # Header with metadata
                st.markdown(f"# {doc_meta['icon']} {doc_meta['title']}")
                if doc_meta.get("description"):
                    st.caption(doc_meta["description"])

                st.markdown("---")

                # Load content
                content = load_doc_content(docs_dir, selected_filename)

                if content:
                    # Render table of contents
                    render_table_of_contents(content)

                    # Remove the first H1 heading (we already display title)
                    lines = content.split("\n")
                    if lines and lines[0].startswith("# "):
                        content = "\n".join(lines[1:])

                    # Render the markdown content
                    st.markdown(content)

                    # Footer with links
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        github_url = f"https://github.com/adamswbrown/azure-architecture-categoriser/blob/main/docs/{selected_filename}"
                        st.markdown(f"[📝 Edit on GitHub]({github_url})")
                    with col2:
                        st.caption(f"Source: `docs/{selected_filename}`")
                else:
                    st.error(f"Could not load content for {selected_filename}")
            else:
                st.warning("Please select a document from the sidebar.")
        else:
            st.info("Select a document from the sidebar to read it.")


if __name__ == "__main__":
    main()
