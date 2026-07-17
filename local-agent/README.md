# JarvisX Local Agent

A fully-automated voice & text AI assistant that answers questions and performs desktop tasks — powered by FastAPI locally and n8n for live internet research, WhatsApp, and email.

---

## Quick Start

```powershell
# From D:\projects\JarvisX
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8000 --app-dir .\local-agent
```

Open Chrome and go to:
```
http://127.0.0.1:8000/ui
```

---

## What JarvisX Can Do

| Command example | What happens |
|---|---|
| `open chrome` | Opens Google Chrome |
| `open notepad` / `open vscode` | Opens that app |
| `search AI news` | Opens Google search in browser |
| `weather in Okara today` | Returns live weather |
| `what is the bitcoin rate` | Fetches live price from CoinGecko via n8n |
| `latest news` | Fetches Google News via n8n |
| `trending songs` | Fetches Apple Music chart via n8n |
| `Tesla stock price` | Fetches via Yahoo Finance via n8n |
| `tell me about Allama Iqbal` | Wikipedia summary via n8n |
| `whatsapp 923001234567 message Salam` | Opens WA Web draft (or auto-sends via n8n) |
| `email to x@example.com subject Hi body Hello` | Opens Gmail draft (or auto-sends via n8n) |
| `what is 144 / 12` | Local math — instant answer |

---

## Architecture

```
Voice/Text UI (browser)
       │
       ▼
JarvisX FastAPI  (:8000)
  ├── planner.py  → detects intent
  ├── executor.py → runs the right tool
  │
  ├── Local tools:  open_app, open_url, web_search, weather, whatsapp, email
  └── n8n tools:
        ├── n8n_router     → news / crypto / stocks / songs / Wikipedia
        ├── n8n_webhook    → generic workflow trigger
        └── (n8n calls back for WhatsApp send, email send)

n8n  (:5678)
  ├── jarvis-router     → live internet research
  ├── jarvis-whatsapp   → Twilio WhatsApp send
  └── jarvis-email      → Gmail send
```

---

## n8n Setup

n8n runs via Docker:
```powershell
cd D:\projects\JarvisX\docker
docker-compose up -d
```

Open n8n at `http://localhost:5678` (user: `admin`, password: `Jarvis123`).

### Import workflows

1. In n8n → **Workflows → Import from file**
2. Import `n8n/jarvis-router.workflow.json` → **Activate**
3. Import `n8n/jarvis-whatsapp.workflow.json` → configure Twilio → **Activate**
4. Import `n8n/jarvis-email.workflow.json` → connect Gmail OAuth2 → **Activate**

---

## Environment Variables

Copy `.env.example` to `.env` and fill in what you need:

```
JARVIS_N8N_ROUTER_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-router
JARVIS_WHATSAPP_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-whatsapp   # optional
JARVIS_EMAIL_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-email         # optional
OPENAI_API_KEY=sk-...                                                        # optional fallback
```

---

## WhatsApp Auto-Send Setup (Twilio)

1. Sign up at [twilio.com](https://www.twilio.com) → get a WhatsApp sandbox number
2. In n8n → **Settings → Environment Variables**, add:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```
3. Set `JARVIS_WHATSAPP_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-whatsapp` in your `.env`

Without these, JarvisX falls back to opening WhatsApp Web with a pre-filled draft.

---

## Gmail Auto-Send Setup

1. In n8n → **Credentials → New → Gmail OAuth2**
2. Connect your Google account
3. Import and activate `n8n/jarvis-email.workflow.json`
4. Set `JARVIS_EMAIL_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-email` in `.env`

Without this, JarvisX opens Gmail compose in the browser.

---

## Voice Input

- Click **🎙 Voice** in the UI
- Allow microphone in Chrome
- Select your language (English / Urdu / Hindi) from the dropdown
- Speak your command — JarvisX will respond both in text and voice
