import streamlit as st
import sqlite3, os
from datetime import datetime
from tools import scrape_website, clean_text

DB_PATH = "leads.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def create_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT,
        emails TEXT,
        scraped TEXT,
        status TEXT,
        notes TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_lead(name, url, emails="", scraped="", status="New", notes=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO leads (name, url, emails, scraped, status, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, url, emails, scraped, status, notes, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def update_lead(lead_id, name, url, emails, status, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    UPDATE leads SET name=?, url=?, emails=?, status=?, notes=? WHERE id=?
    """, (name, url, emails, status, notes, lead_id))
    conn.commit()
    conn.close()

def delete_lead(lead_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM leads WHERE id=?", (lead_id,))
    conn.commit()
    conn.close()

def fetch_leads(limit=200):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, url, emails, status, notes, created_at FROM leads ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def show_dashboard():
    st.subheader("📊 Deal Closing CRM")
    create_table()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Add Lead")
        with st.form("add_lead_form", clear_on_submit=True):
            name = st.text_input("Company / Lead name")
            url = st.text_input("Website URL (include https://)")
            emails = st.text_input("Contact emails (comma separated)")
            notes = st.text_area("Notes")
            status = st.selectbox("Status", ["New", "Contacted", "Interested", "Won", "Lost"]) 
            submitted = st.form_submit_button("Add Lead")
        if submitted:
            if not name and not url:
                st.error("Please provide at least a name or a URL.")
            else:
                add_lead(name or url, url, emails, "", status, notes)
                st.success("Lead added.")
                st.experimental_rerun()

        st.markdown("---")
        st.markdown("### Run Crew (Scrape a website and create a lead)")
        run_url = st.text_input("Enter URL to scrape:", key="run_url_field")
        if st.button("Run Crew (Scrape & Add)"):
            if not run_url:
                st.error("Enter a URL to scrape.")
            else:
                try:
                    raw = scrape_website(run_url)
                    cleaned = clean_text(raw)[:4000]
                    display_name = run_url.split("//")[-1].split("/")[0]
                    add_lead(display_name, run_url, "", cleaned, "New", "Added by Run Crew")
                    st.success(f"Scraped and added lead: {display_name}")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Scrape failed: {e}")

    with col2:
        st.markdown("### Leads")
        rows = fetch_leads()
        if not rows:
            st.info("No leads yet. Add a lead or run the scraper.")
        else:
            for row in rows:
                lead_id, name, url, emails, status, notes, created_at = row
                with st.expander(f"{name} — {status} — {created_at}"):
                    st.write("**URL:**", url)
                    st.write("**Emails:**", emails)
                    st.write("**Notes:**", notes)
                    cols = st.columns([1,1,1,1])
                    if cols[0].button("Edit", key=f"edit_{lead_id}"):
                        new_name = st.text_input("Name", value=name, key=f"name_{lead_id}")
                        new_url = st.text_input("URL", value=url, key=f"url_{lead_id}")
                        new_emails = st.text_input("Emails", value=emails, key=f"emails_{lead_id}")
                        new_status = st.selectbox("Status", ["New","Contacted","Interested","Won","Lost"], index=["New","Contacted","Interested","Won","Lost"].index(status if status in ["New","Contacted","Interested","Won","Lost"] else "New"), key=f"status_{lead_id}")
                        new_notes = st.text_area("Notes", value=notes, key=f"notes_{lead_id}")
                        if st.button("Save", key=f"save_{lead_id}"):
                            update_lead(lead_id, new_name, new_url, new_emails, new_status, new_notes)
                            st.success("Lead updated.")
                            st.experimental_rerun()
                    if cols[1].button("Delete", key=f"delete_{lead_id}"):
                        delete_lead(lead_id)
                        st.warning("Lead deleted.")
                        st.experimental_rerun()
                    if cols[2].button("Copy URL", key=f"copy_{lead_id}"):
                        st.write("URL copied — use your browser to copy the text below:")
                        st.code(url)
                    if cols[3].button("Show Scraped Text", key=f"scrape_{lead_id}"):
                        conn = get_conn()
                        c = conn.cursor()
                        c.execute("SELECT scraped FROM leads WHERE id=?", (lead_id,))
                        scraped_text = c.fetchone()
                        conn.close()
                        if scraped_text and scraped_text[0]:
                            st.text_area("Scraped text (truncated)", scraped_text[0][:4000])
                        else:
                            st.info("No scraped text stored for this lead.")
