# Deal Closing AI — Ready-to-deploy (Streamlit + SQLite)

## How to deploy to Render (summary)
1. Create a new GitHub repo and push these files.
2. On Render: New -> Web Service -> Connect GitHub -> select repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. Deploy. The app comes with a sample `leads.db` so the dashboard is pre-populated.

## Notes
- This demo uses SQLite stored in the repo; for production use a managed DB (Supabase/Postgres).
- Keep your secrets out of the repo. Use Render environment variables for credentials.
