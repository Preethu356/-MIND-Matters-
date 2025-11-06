# MH Consult — Mental Health Consultation & Counselling (Streamlit)

## Overview
This repository contains a demo/starting point for a mental health consultation and counselling web app built with Streamlit and optionally integrated with OpenAI for chatbot responses.

**Important:** This project is for educational/demo purposes. Do NOT use this app as a replacement for licensed mental health care. Add clear crisis hotlines and comply with local regulations before deploying publicly.

## Files
- `app.py` — main Streamlit app with chat UI and OpenAI integration
- `helpers.py` — utility functions
- `config.toml` — sample configuration
- `requirements.txt` — Python dependencies
- `deploy_instructions.txt` — deployment steps for Streamlit Cloud & Heroku
- `Procfile`, `runtime.txt` — optional Heroku files
- `.github/workflows/python-app.yml` — simple CI example
- `assets/` — placeholder for images and logos

## Setup (local)
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate    # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Create a `.env` file with:
   ```
   OPENAI_API_KEY=sk-...
   ```
   This file is included in `.gitignore` so it won't be committed.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## OpenAI API key & security
- Do not hardcode your API key.
- When deploying to Streamlit Community Cloud, add `OPENAI_API_KEY` as a secret (App settings -> Secrets).
- For GitHub Actions or Heroku, store secrets in their secure settings and reference them only at runtime.

## Suggested improvements
- Persistent storage (SQLite, Supabase, or Google Sheets) for logs (ensure data privacy).
- Professional review of content and safety flows.
- Localization and accessibility improvements.
- Proper legal & compliance checks before production.

## License
MIT
