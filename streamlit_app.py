import streamlit as st
import dashboard, agents, tools

st.set_page_config(page_title="Deal Closing AI", layout="wide")
st.title("🤝 Deal Closing AI Platform")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Agents", "Tools", "About"])

if menu == "Dashboard":
    dashboard.show_dashboard()
elif menu == "Agents":
    agents.show_agents()
elif menu == "Tools":
    selected_tool = st.selectbox("Select a Tool", tools.get_all_tools())
    if st.button("Run Tool"):
        result = tools.run_tool(selected_tool)
        st.success(result)
else:
    st.markdown("""
    ### About
    This is a ready-to-deploy demo **Deal Closing CRM** (Streamlit + SQLite).
    - Add leads, edit, delete, and run a simple website scraper.
    - Uses SQLite (`leads.db`) so no external DB setup is required.
    """)
