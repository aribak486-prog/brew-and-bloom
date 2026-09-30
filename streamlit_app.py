"""Minimal Streamlit Cloud wrapper for the Brew & Bloom repository.

Streamlit Community Cloud runs this Python entry point. The existing Next.js
frontend and FastAPI backend remain separate applications and are not started
or modified by this wrapper.
"""

import os
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st


ROOT = Path(__file__).resolve().parent
FRONTEND_FILES = ("app/page.tsx", "app/layout.tsx", "package.json")
BACKEND_FILES = ("backend/app/main.py", "backend/requirements.txt")


def frontend_url() -> str:
    """Read only the public website URL, never backend credentials or secrets."""
    configured = os.environ.get("BREW_BLOOM_FRONTEND_URL", "").strip()
    try:
        configured = st.secrets.get("BREW_BLOOM_FRONTEND_URL", configured).strip()
    except Exception:
        # A local Streamlit run may not have a secrets.toml file.
        pass

    parsed = urlsplit(configured)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    if parsed.username or parsed.password:
        return ""
    return configured


site = frontend_url()
st.set_page_config(page_title="Brew & Bloom", page_icon="☕", layout="wide")

if site:
    st.link_button("Open Brew & Bloom Website", site, type="primary")
    st.caption("If the embedded site is blocked by the host, use the button above to open it directly.")
    st.iframe(site, height=1050)
else:
    st.title("Brew & Bloom")
    st.caption("Streamlit deployment wrapper")
    st.info(
        "This repository's cafe website uses a Next.js frontend and a FastAPI backend. "
        "Streamlit Community Cloud runs this Python page; it does not build or host the "
        "Next.js and FastAPI services automatically. The existing application source is left intact."
    )

    left, right = st.columns(2)
    with left:
        frontend_found = all((ROOT / path).is_file() for path in FRONTEND_FILES)
        st.metric("Next.js frontend", "Found" if frontend_found else "Not found")
    with right:
        backend_found = all((ROOT / path).is_file() for path in BACKEND_FILES)
        st.metric("FastAPI backend", "Found" if backend_found else "Not found")

    st.warning(
        "The website URL is not configured. To link to the full site, deploy the existing "
        "Next.js frontend separately, then add BREW_BLOOM_FRONTEND_URL in Streamlit Cloud secrets."
    )

    with st.expander("How this deployment works"):
        st.markdown(
            "- **Streamlit main file:** `streamlit_app.py`\n"
            "- **Streamlit Cloud branch:** `main`\n"
            "- **Existing frontend:** Next.js; deploy it on a Node.js-capable host.\n"
            "- **Existing backend:** FastAPI; deploy it on a Python API host with its PostgreSQL and Stripe configuration.\n"
            "- This wrapper embeds and links to the public frontend when `BREW_BLOOM_FRONTEND_URL` is configured. "
            "It does not launch subprocesses, expose environment values, or change application files."
        )
