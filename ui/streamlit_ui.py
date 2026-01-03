import streamlit as st
from utils.streamlit_helpers import get_category_color


def render_program(program):
    color = get_category_color(program.ebene)

    with st.container():
        st.markdown(
            f"<div style='border-left: 6px solid {color}; padding: 8px;'>",
            unsafe_allow_html=True
        )

        st.markdown(f"### {program.name} ({program.ebene})")
        st.markdown(f"**Förderhöhe:** {program.foerderhoehe}")
        st.markdown(f"**Warum geeignet:** {program.begruendung}")

        if st.button("🔍 Details ansehen", key=program.name):
            st.session_state["selected_program"] = program

        st.markdown("</div>", unsafe_allow_html=True)

