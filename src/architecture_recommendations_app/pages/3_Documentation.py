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


def render_sidebar_navigation(available_docs: list[dict], filtered_docs: list[dict]) -> None:
    """Render the documentation navigation in the sidebar."""
    with st.sidebar:
        st.markdown("## 📖 Documentation")
        st.caption("Browse project documentation")

        # Search
        search_term = st.text_input(
            "Search docs",
            placeholder="Search...",
            label_visibility="collapsed",
            key="doc_search"
        )

        # Filter docs by search
        if search_term:
            filtered_docs = [
                d for d in available_docs
                if search_term.lower() in d["title"].lower()
                or search_term.lower() in d.get("description", "").lower()
            ]

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
                st.markdown(f"**{category}**")

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

                st.markdown("")  # Spacer between categories

        # Handle "Other" category
        if "Other" in docs_by_category:
            st.markdown("**Other**")
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

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 0.5rem 0; color: #666; font-size: 0.8rem;">
                <p style="margin-bottom: 0.5rem;">
                    Built by <a href="https://askadam.cloud/#about" target="_blank"><strong>Adam Brown</strong></a>
                </p>
                <a href="https://github.com/adamswbrown/azure-architecture-categoriser" target="_blank">
                    <img src="https://img.shields.io/badge/GitHub-181717?style=flat&logo=github" alt="GitHub"/>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    st.set_page_config(
        page_title="Documentation - Azure Architecture Recommendations",
        page_icon="📖",
        layout="wide",
    )

    # Custom CSS for documentation styling
    st.markdown("""
    <style>
    /* Hide default sidebar decorations for cleaner look */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar button styling */
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.9rem !important;
    }

    /* Main content max width for readability */
    .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

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

    # Render navigation in sidebar (sticky by default)
    render_sidebar_navigation(available_docs, available_docs)

    # Main content area
    selected_filename = st.session_state.get("selected_doc")

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
