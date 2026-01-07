"""
Streamlit App: Resume-JD Ranking & Fairness Audit Demo

Purpose: Interactive demonstration of ranking behavior and bias sensitivity.
Philosophy: Responsible ML audit & observability (internal tooling feel)
NOT a hiring tool - for evaluation and transparency only.
"""

import streamlit as st
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.semantic_model import SemanticRanker
from src.models.tfidf_ranker import TFIDFRanker
from src.models.hybrid_ranker import HybridRanker
from src.fairness.perturbations import (
    gender_pronoun_swap,
    redact_names,
    swap_university,
    insert_gap
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config - clean, professional
st.set_page_config(
    page_title="Resume Ranking Audit Demo",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for calm, neutral theme + responsive branding
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 4px;
        padding: 12px 24px;
        border: 1px solid #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4a5568;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #2d3748;
    }
    .audit-note {
        background-color: #f0f4f8;
        padding: 16px;
        border-radius: 4px;
        border-left: 4px solid #4a5568;
        color: #4a5568;
        font-size: 0.9rem;
        margin: 16px 0;
    }
    .author-name-full {
        display: inline;
        color: #4a5568;
        font-size: 0.85rem;
        font-weight: 500;
        margin-left: 8px;
    }
    .author-name-short {
        display: none;
    }
    @media (max-width: 768px) {
        .author-name-full {
            display: none;
        }
        .author-name-short {
            display: inline;
            color: #4a5568;
            font-size: 0.85rem;
            font-weight: 500;
            margin-left: 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Top Header (non-negotiable)
st.markdown(
    "# Resume-JD Ranking & Fairness Audit Demo"
    '<span class="author-name-full">— Mounusha Ram Metti</span>'
    '<span class="author-name-short">— MR</span>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="color: #718096; font-size: 0.95rem; margin-top: -12px;">'
    'Interactive demonstration of ranking behavior and bias sensitivity. '
    '<strong>This system does not make hiring decisions.</strong>'
    '</p>',
    unsafe_allow_html=True
)

# Load models (cached)
@st.cache_resource
def load_models():
    """Load and cache ranking models."""
    # Load resumes for fitting
    with open("data/processed/resumes.json", "r") as f:
        resumes = json.load(f)
    
    # Semantic model
    semantic_model = SemanticRanker(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )
    semantic_model.fit(resumes)
    
    # TF-IDF baseline
    tfidf_model = TFIDFRanker(max_features=5000, ngram_range=(1, 2))
    tfidf_model.fit(resumes)
    
    # Hybrid model (production-realistic)
    hybrid_model = HybridRanker(
        semantic_ranker=semantic_model,
        weights={
            "semantic": 0.70,
            "education": 0.15,
            "continuity": 0.10,
            "other": 0.05
        }
    )
    hybrid_model.fit(resumes)
    
    return semantic_model, tfidf_model, hybrid_model, resumes

@st.cache_data
def load_job_descriptions():
    """Load job descriptions."""
    with open("data/processed/job_descriptions.json", "r") as f:
        return json.load(f)

# Load data
with st.spinner("Loading evaluation models..."):
    semantic_model, tfidf_model, hybrid_model, resumes = load_models()
    job_descriptions = load_job_descriptions()

# Model selector in expander (minimal UI)
with st.expander("⚙️ Model Configuration", expanded=False):
    model_choice = st.selectbox(
        "Ranking Model",
        ["Hybrid (Production)", "Semantic (SBERT)", "TF-IDF Baseline"],
        help="Select the ranking algorithm for evaluation"
    )
    
    if model_choice == "Hybrid (Production)":
        model = hybrid_model
        st.caption("70% semantic + 15% education + 10% continuity + 5% other")
    elif model_choice == "Semantic (SBERT)":
        model = semantic_model
        st.caption("Pure SBERT embeddings (implicit signals only)")
    else:
        model = tfidf_model
        st.caption("Sparse bag-of-words representation")

# Main tabs - TWO ONLY
tab1, tab2 = st.tabs(["📄 Ranking Demo", "🧪 Fairness & Stability Audit"])

# ========== TAB 1: Ranking Demo (SECONDARY FEATURE - Context) ==========
with tab1:
    st.markdown("### Ranking Demo")
    st.caption("Shows how resumes are ranked by relevance. Provides context for fairness audit.")
    
    # Job Description Input
    st.markdown("#### Job Description (example input)")
    
    # Pre-filled example
    example_jd = next((jd for jd in job_descriptions if "data scientist" in jd.get("title", "").lower()), job_descriptions[0])
    
    jd_input = st.text_area(
        "Enter or modify job description",
        value=example_jd["text"][:500] + "...",
        height=180,
        label_visibility="collapsed"
    )
    
    # Resume Selection (keep it small)
    st.markdown("#### Candidate Resumes (demo subset)")
    num_resumes = st.slider("Number of resumes to rank", 3, 10, 5, label_visibility="collapsed")
    st.caption(f"Ranking top {num_resumes} from {len(resumes)} total (demo purposes)")
    
    # Run Ranking Button
    if st.button("Run Relevance Ranking", type="primary", use_container_width=True):
        with st.spinner("Computing rankings..."):
            # Rank resumes
            rankings = model.rank(jd_input, resumes)
            top_rankings = rankings[:num_resumes]
            
            st.markdown("#### Ranking Results")
            
            # Clean table
            results_data = []
            for rank, (resume_id, score) in enumerate(top_rankings, 1):
                resume = next(r for r in resumes if r["id"] == resume_id)
                
                # Extract top skills (simple keyword extraction)
                text = resume["text"].lower()
                skills = []
                skill_keywords = ["python", "machine learning", "sql", "java", "data", "analysis"]
                for skill in skill_keywords:
                    if skill in text:
                        skills.append(skill)
                
                results_data.append({
                    "Rank": rank,
                    "Resume ID": resume_id,
                    "Relevance Score": f"{score:.3f}",
                    "Top Matching Skills": ", ".join(skills[:3]) if skills else "—"
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Important note
            st.markdown(
                '<div class="audit-note">'
                '<strong>Note:</strong> Scores reflect semantic relevance, not hiring suitability. '
                'This is a demonstration of ranking behavior, not a recommendation system.'
                '</div>',
                unsafe_allow_html=True
            )

# ========== TAB 2: Fairness & Stability Audit (⭐ MAIN FEATURE) ==========
with tab2:
    st.markdown("### Fairness & Stability Audit")
    st.caption("Evaluate model sensitivity to non-skill attribute changes. This is for transparency and evaluation.")
    
    # Audit Context Inputs
    st.markdown("#### Audit Scenario")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Job description (same as tab 1)
        audit_jd_titles = [jd["title"] for jd in job_descriptions if jd.get("title")]
        audit_jd_title = st.selectbox("Job Description", audit_jd_titles[:10], label_visibility="collapsed")
        audit_jd = next(jd for jd in job_descriptions if jd.get("title") == audit_jd_title)
        st.caption(f"Selected: {audit_jd_title}")
    
    with col2:
        # One base resume
        resume_idx = st.number_input("Base Resume Index", 0, min(100, len(resumes)-1), 0, label_visibility="collapsed")
        test_resume = resumes[resume_idx]
        st.caption(f"Resume ID: {test_resume['id']}")
    
    # Show base resume preview
    with st.expander("View Base Resume (preview)", expanded=False):
        st.text_area("", test_resume["text"][:500] + "...", height=200, disabled=True, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Counterfactual test selection
    st.markdown("#### Select Counterfactual Test")
    
    test_type = st.selectbox(
        "Fairness Dimension",
        [
            "University Prestige Swap",
            "Employment Gap Insertion",
            "Gender Pronoun Test",
            "Name Redaction"
        ],
        label_visibility="collapsed"
    )
    
    # Test parameters
    if "University" in test_type:
        variant_desc = "Elite institution → Standard institution"
        variant_param = "Tier3_Standard"
    elif "Employment Gap" in test_type:
        gap_months = st.slider("Gap Duration (months)", 3, 24, 12)
        variant_desc = f"{gap_months}-month employment gap inserted"
        variant_param = gap_months
    elif "Gender" in test_type:
        gender_choice = st.radio("Pronoun variant", ["Male (he/him)", "Female (she/her)"], horizontal=True)
        variant_desc = f"Gender pronouns: {gender_choice.split()[0].lower()}"
        variant_param = "male" if "Male" in gender_choice else "female"
    else:  # Name redaction
        variant_desc = "All names redacted to [NAME]"
        variant_param = None
    
    st.caption(f"Variant: {variant_desc}")
    
    # Run Audit Button
    if st.button("Run Counterfactual Audit", type="primary", use_container_width=True):
        with st.spinner("Running audit..."):
            # Create variant
            original_text = test_resume["text"]
            
            if "University" in test_type:
                variant_text = swap_university(original_text, variant_param)
            elif "Employment Gap" in test_type:
                variant_text = insert_gap(original_text, gap_length_months=variant_param)
            elif "Gender" in test_type:
                direction = "to_male" if variant_param == "male" else "to_female"
                variant_text = gender_pronoun_swap(original_text, direction=direction)
            else:  # Name redaction
                variant_text = redact_names(original_text)
            
            # Create variant resume
            variant_resume = {
                "id": test_resume["id"] + "_variant",
                "text": variant_text
            }
            
            # Rank both
            original_ranking = model.rank(audit_jd["text"], resumes)
            variant_ranking = model.rank(audit_jd["text"], [variant_resume] + [r for r in resumes if r["id"] != test_resume["id"]])
            
            # Find ranks and scores
            original_rank = next((i+1 for i, (rid, _) in enumerate(original_ranking) if rid == test_resume["id"]), None)
            variant_rank = next((i+1 for i, (rid, _) in enumerate(variant_ranking) if rid == variant_resume["id"]), None)
            
            original_score = next((s for rid, s in original_ranking if rid == test_resume["id"]), 0)
            variant_score = next((s for rid, s in variant_ranking if rid == variant_resume["id"]), 0)
            
            # Calculate changes
            rank_change = variant_rank - original_rank
            score_change = variant_score - original_score
            
            st.markdown("---")
            st.markdown("#### Audit Results")
            
            # Counterfactual Variants Table
            st.markdown("**Counterfactual Variants**")
            variants_df = pd.DataFrame([
                {
                    "Variant": "Original",
                    "Changed Attribute": "None",
                    "Description": "Base resume"
                },
                {
                    "Variant": "Modified",
                    "Changed Attribute": test_type.replace(" Test", "").replace(" Swap", "").replace(" Insertion", ""),
                    "Description": variant_desc
                }
            ])
            st.dataframe(variants_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Results Panel (THREE THINGS ONLY)
            st.markdown("**Change Summary**")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Original Rank", f"#{original_rank}", help="Position in ranking before modification")
            
            with metric_col2:
                st.metric("Modified Rank", f"#{variant_rank}", delta=f"{rank_change:+d} positions")
            
            with metric_col3:
                score_pct = (score_change / original_score * 100) if original_score > 0 else 0
                st.metric("Score Change", f"{score_change:+.3f}", delta=f"{score_pct:+.1f}%")
            
            # Visualization (existing bar chart)
            st.markdown("**Sensitivity Visualization**")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Rank Change", "Score Change (×10)"],
                y=[abs(rank_change), abs(score_change * 10)],
                marker_color=['#718096', '#4a5568'],
                text=[f"{rank_change:+d}", f"{score_change:+.2f}"],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Magnitude of Changes",
                yaxis_title="Absolute Change",
                showlegend=False,
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Interpretation Box (static, professional)
            st.markdown(
                '<div class="audit-note">'
                '<strong>How to interpret this:</strong><br>'
                'Changes indicate sensitivity of the ranking model to non-skill attributes. '
                'Larger changes suggest the model is influenced by factors unrelated to job qualifications. '
                'This demo is for evaluation and transparency, not decision-making.'
                '</div>',
                unsafe_allow_html=True
            )

# Footer
st.markdown("---")
st.markdown(
    '<p style="color: #a0aec0; font-size: 0.85rem; text-align: center;">'
    'This tool is for evaluation and research purposes only. '
    'It does not make hiring recommendations and should not be used for employment decisions.'
    '</p>',
    unsafe_allow_html=True
)
