import streamlit as st
from graph import app

st.set_page_config(page_title="AI Roadmap Planner", layout="wide")

st.title("🚀 AI Roadmap Planner")
st.caption("Structured Planning Engine with Human-in-the-Loop Refinement")


# ---------------- DEFAULT SESSION STATE ---------------- #

default_state = {
    "goal": "",
    "current_level": "",
    "strengths": "",
    "weaknesses": "",
    "deadline": "",
    "additional_constraints": "",
    "structured_plan": {},
    "formatted_plan": "",
    "modification_request": "",
    "plan_history": [],
    "show_modify": False,
}   

for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- RESET ---------------- #

if st.button("🔄 Start New Plan"):
    for key in default_state:
        st.session_state[key] = default_state[key]
    st.rerun()


# ---------------- INPUT FORM ---------------- #

if not st.session_state.plan_history:

    with st.form("planner_form"):

        st.subheader("📋 Fill Planning Details")

        goal = st.text_input("🎯 Goal")
        current_level = st.text_input("📊 Current Skill Level")
        strengths = st.text_area("💪 Strengths")
        weaknesses = st.text_area("⚠ Weaknesses")
        deadline = st.selectbox(
        "📅 Deadline",
        [
            "2 month",
            "4 months",
            "6 months",
        ]
        )

        constraints = st.text_area("📌 Additional Constraints")

        submitted = st.form_submit_button("Generate Plan")

        if submitted:

            # Save user input to session
            st.session_state.goal = goal
            st.session_state.current_level = current_level
            st.session_state.strengths = strengths
            st.session_state.weaknesses = weaknesses
            st.session_state.deadline = deadline
            st.session_state.additional_constraints = constraints

            with st.spinner("Generating structured plan..."):

                result = app.invoke({
                    **st.session_state,
                    "modification_request": "",
                })

            st.session_state.plan_history = result.get("plan_history", [])
            st.session_state.structured_plan = result.get("structured_plan", {})
            st.rerun()


# ---------------- DISPLAY HISTORY ---------------- #

if st.session_state.plan_history:

    st.subheader("📌 Version History (HITL Evolution)")

    total_versions = len(st.session_state.plan_history)

    for idx, plan in enumerate(st.session_state.plan_history):

        is_latest = idx == total_versions - 1

        if is_latest:
            st.markdown(f"### 🟢 Version {idx+1} (Latest)")
            st.markdown(plan)
            st.divider()
        else:
            with st.expander(f"🔵 Version {idx+1}"):
                st.markdown(plan)

    st.divider()

    if st.button("✏ Modify Latest Plan"):
        st.session_state.show_modify = True

    if st.session_state.show_modify:

        modification = st.text_area("What would you like to change?")

        if st.button("Apply Modification"):

            with st.spinner("Refining plan..."):

                result = app.invoke({
                    **st.session_state,
                    "modification_request": modification,
                })

            st.session_state.plan_history = result.get("plan_history", [])
            st.session_state.structured_plan = result.get("structured_plan", {})
            st.session_state.show_modify = False

            st.rerun()
