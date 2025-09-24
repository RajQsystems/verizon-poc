import streamlit as st

st.set_page_config(
    page_title="Verizon New Build Intelligence — Dynamic Reporting",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Brand / Hero Header
# =========================
st.markdown(
    """
    <style>
    .hero {
        padding: 2.2rem 2.0rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #0a0f1f 0%, #101a3a 60%, #132047 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .hero h1 {
        font-size: 2.0rem;
        margin: 0 0 0.6rem 0;
        line-height: 1.2;
    }
    .hero p {
        font-size: 1.0rem;
        opacity: 0.92;
        margin: 0.2rem 0 0 0;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        margin-right: 0.4rem;
    }
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        background: #e9eefb;
        color: #23376b;
        border: 1px solid #d4def7;
        margin-right: 0.4rem;
    }
    .section {
        padding: 1.2rem 1.0rem;
        border-radius: 12px;
        border: 1px solid #eaecef;
        background: #ffffff;
    }
    .muted {
        color: #5f6b7a;
        font-size: 0.95rem;
    }
    .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
    .card {
        padding: 1.0rem;
        border-radius: 12px;
        border: 1px solid #eaecef;
        background: #fcfdff;
    }
    .small {
        font-size: 0.88rem;
        color: #5f6b7a;
    }
    hr.soft {
        border: none;
        border-top: 1px dashed #e6e9ef;
        margin: 1.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown(
        """
        <div class="hero">
            <div class="badge">Internal</div>
            <h1>Verizon New Build Intelligence — Dynamic Reporting</h1>
            <p>Experience a focused, role-aware reporting interface designed to describe goals, scope, and usage without performing any calculations.</p>
            <div style="margin-top: 0.8rem;">
                <span class="pill">New Build</span>
                <span class="pill">Workflow-Aware</span>
                <span class="pill">Role-Based</span>
                <span class="pill">Dashboard Ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Intro / Overview
# =========================
st.markdown("")
left, right = st.columns([1.2, 1])

with left:
    st.markdown("### Overview")
    st.markdown(
        """
        This interface presents a home experience for dynamic reporting across Verizon New Build activities. 
        It introduces the project intent, audience, and the kinds of reports envisioned, while deliberately avoiding any data computation. 
        """
    )
    st.markdown(
        """
        The page is intentionally descriptive, outlining the eventual report types (e.g., anomaly highlights, cycle-time views, SLA risk summaries, and market/vendor comparisons) 
        that would be accessible in a full build, with no processing performed here.
        """
    )

with right:
    st.markdown("### Quick Facts")
    st.markdown(
        """
        - Project: Verizon New Build Intelligence — Dynamic Reporting  
        - Version: 0.1 (Home only)  
        - Mode: Non-computational (Design & Description)  
        - Focus: Clarity, roles, and report catalog  
        """
    )

st.markdown("")

# =========================
# Purpose & Scope
# =========================
st.markdown("### Purpose")
st.markdown(
    """
    Present a cohesive, branded home page that communicates the objectives and the high-level user journey for stakeholders and contributors, 
    establishing a shared understanding before implementation of interactive analytics.
    """
)

st.markdown("### Scope")
st.markdown(
    """
    - Describe intended report categories and role-based views  
    - Outline the user experience and navigation patterns  
    - Provide a consistent visual foundation with badges, cards, and sections  
    - Exclude computations, data processing, and live integrations  
    """
)

st.markdown("")

# =========================
# Audience & Roles
# =========================
st.markdown("### Audience")
st.markdown(
    """
    - Real Estate, Regulatory, and Construction stakeholders  
    - Market operations and vendor management teams  
    - Program managers and leadership reviewing direction  
    """
)

st.markdown("### Role Views")
st.markdown(
    """
    - Real Estate: Pipeline visualization, milestone summaries, descriptive risk language  
    - Regulatory: Compliance checkpoints and descriptive status narratives  
    - Construction: Readiness and progress storytelling without KPIs  
    """
)

st.markdown("")

# =========================
# Report Catalog (Descriptive)
# =========================
st.markdown("### Report Catalog")
st.markdown(
    """
    The interface envisions these report areas. This home page lists descriptions only—no data is processed.
    """
)

st.markdown(
    """
    - Overview: A narrative snapshot of portfolio health and recent updates  
    - Milestones: Plain-language timelines and phase descriptions  
    - Risk & SLA: Qualitative risk categories and what they imply for attention  
    - Vendors & Markets: Textual summaries of patterns to watch by vendor and market  
    - Activity Log: Descriptive recent changes and notable events  
    """
)

st.markdown("")
st.markdown("---")
st.markdown(
    "Made with ❤️ for teams delivering clarity first. This home focuses on narrative and design, without calculations."
)
# =========================
