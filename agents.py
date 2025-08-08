import streamlit as st
from tools import clean_text

def show_agents():
    st.subheader("🤖 AI Agents (placeholders)")
    st.write("These are placeholder agent actions for demo purposes.")

    agent = st.selectbox("Choose an agent to run:", ["Lead Scraper", "Pitch Writer", "Follow-up Sender"]) 
    if st.button("Run Agent"):
        if agent == "Lead Scraper": 
            st.info("Use 'Run Crew' on the Dashboard to scrape and add leads.")
        elif agent == "Pitch Writer": 
            st.code("Hello {name},\n\nWe can help you improve conversions by 20%.")
        elif agent == "Follow-up Sender": 
            st.success("Follow-up template created. Use your own SMTP to send emails.")
