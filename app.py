import re
import streamlit as st
import langchain
from graph import build_graph

langchain.debug = True

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1e293b 100%);
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 1.2rem;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(124,58,237,0.16));
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.20);
    }

    .section-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px;
        margin-top: 12px;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }

    .small-note {
        color: #cbd5e1;
        font-size: 0.92rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 0.8rem 1rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        box-shadow: 0 8px 20px rgba(37,99,235,0.35);
    }

    .stButton > button:hover {
        filter: brightness(1.05);
    }

    div[data-baseweb="textarea"] textarea {
        border-radius: 14px !important;
        background-color: rgba(255,255,255,0.03) !important;
    }
</style>
""", unsafe_allow_html=True)


def extract_basic_fields(user_query: str):
    # Simple fallback parsing so the graph starts with useful state.
    days = 3
    budget = 0.0

    day_match = re.search(r"(\d+)\s*day", user_query, re.I)
    if day_match:
        days = int(day_match.group(1))

    budget_match = re.search(r"(\d+(?:,\d+)?(?:\.\d+)?)", user_query.replace(",", ""))
    if budget_match:
        try:
            budget = float(budget_match.group(1))
        except Exception:
            budget = 0.0

    return days, budget


def main():
    st.markdown("""
    <div class="hero-box">
        <div class="main-title">✈️ AI Travel Planner</div>
        <div class="subtitle">
            Plan smarter trips with dynamic agent thinking, live execution flow, and a clean travel planning dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.25, 0.75], gap="large")

    with col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Travel Request</div>', unsafe_allow_html=True)

        user_query = st.text_area(
            "Enter your travel request:",
            height=150,
            placeholder="Plan a 4 day trip to Goa under 25000 INR with beaches, seafood, sunset spots, and not too much walking"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Generate Travel Plan"):
            if not user_query.strip():
                st.warning("Please enter your travel request.")
                return

            app = build_graph()
            days, budget = extract_basic_fields(user_query)

            input_state = {
                "user_query": user_query,
                "days": days,
                "budget": budget,
                "research_notes": "",
                "itinerary": "",
                "budget_breakdown": "",
                "validation_notes": ""
            }

            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Agent Thinking</div>', unsafe_allow_html=True)

            thinking_placeholder = st.empty()

            logs = []

            for event in app.stream(input_state):
                for node, output in event.items():
                    logs.append(f"--- {node.upper()} ---\n{output}\n")
                    thinking_placeholder.code("\n".join(logs))

            st.success("EXECUTION COMPLETE")
            st.markdown('</div>', unsafe_allow_html=True)

            result = app.invoke(input_state)

            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Final Travel Answer</div>', unsafe_allow_html=True)
            st.write(result.get("final_answer", "No answer generated."))
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-box">
            <div class="section-title">Quick Guide</div>
            <div class="small-note">
                Write your request clearly with:
                <br><br>
                • destination<br>
                • number of days<br>
                • budget<br>
                • interests<br>
                • constraints
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-box">
            <div class="section-title">Example Prompt</div>
            <div class="small-note">
                Plan a 5 day trip to Jaipur under 18000 INR with forts, food, shopping, and low walking.
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()