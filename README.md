# JarvisX — Fully Automated Voice AI Assistant 🎤🤖

**JarvisX** is a fully-automated voice and text AI assistant that combines local desktop automation with live internet intelligence via n8n. Ask questions, perform tasks, send messages — all in natural language using voice or text.

---

## 🎯 What JarvisX Can Do

### Local Desktop Automation
- **Open apps:** Chrome, VS Code, Notepad, Word, Excel, PowerPoint, Spotify, VLC, Telegram, File Explorer, Task Manager
- **Web search:** Opens Google search in browser
- **Open URLs:** Opens any website in Chrome
- **Math calculations:** Instant answers for arithmetic

### Live Internet Intelligence (via n8n)
- **Bitcoin & Crypto rates:** Real-time prices from CoinGecko (Bitcoin, Ethereum, BNB, DOGE, Solana) in USD + PKR
- **Stock prices:** Live data from Yahoo Finance (Tesla, Apple, Microsoft, NVIDIA, Meta, Amazon, etc.)
- **Latest news:** Google News RSS — latest headlines on any topic
- **Trending songs:** Apple Music top charts
- **Wikipedia summaries:** Quick info on people, places, concepts
- **Weather:** Live weather for any city (OpenWeatherMap)

### Communication
- **WhatsApp messages:** Opens WhatsApp Web draft (or auto-sends via Twilio when configured)
- **Email:** Opens Gmail compose (or auto-sends via Gmail OAuth2 when configured)

---

## 🚀 Quick Start

### 1. Start the Local Agent

```powershell
# From D:\projects\JarvisX
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8000 --app-dir .\local-agent
```

### 2. Start n8n (Docker)

```powershell
cd docker
docker-compose up -d
```

- n8n runs at `http://localhost:5678`
- Login: `admin` / `Jarvis123`

### 3. Import n8n Workflows

1. Open n8n → **Workflows → Import from file**
2. Import `n8n/jarvis-router.workflow.json` → **Activate**
3. Import `n8n/jarvis-whatsapp.workflow.json` → configure Twilio → **Activate** (optional)
4. Import `n8n/jarvis-email.workflow.json` → connect Gmail → **Activate** (optional)

### 4. Open JarvisX UI

Open Chrome and go to:
```
http://127.0.0.1:8000/ui
```

- Click **🎙 Voice** to use voice input
- Select your language (English / Urdu / Hindi / Arabic)
- Speak or type your command

---

## 📋 Example Commands

| Command | What Happens |
|---------|--------------|
| `open chrome` | Opens Google Chrome |
| `open file explorer` | Opens Windows Explorer |
| `search AI news` | Opens Google search |
| `weather in Lahore today` | Returns live weather |
| `bitcoin rate` | Returns live Bitcoin price (USD + PKR) via n8n |
| `Tesla stock price` | Returns live stock price via n8n |
| `latest news` | Returns top headlines via n8n |
| `trending songs` | Returns Apple Music top charts via n8n |
| `tell me about Allama Iqbal` | Returns Wikipedia summary via n8n |
| `whatsapp 923001234567 message Salam` | Opens WhatsApp Web draft (or auto-sends) |
| `email to x@example.com subject Hi body Hello` | Opens Gmail draft (or auto-sends) |
| `what is 144 / 12` | Returns instant math answer (local) |

---

## 🏗️ Architecture

```
Voice/Text UI (Browser)
       │
       ▼
JarvisX FastAPI (:8000)
  ├── planner.py      → Intent detection & routing
  ├── executor.py     → Tool execution
  ├── Local tools:    open_app, open_url, web_search, weather
  └── n8n tools:      n8n_router (internet research)
       
       ▼
n8n (:5678)
  ├── jarvis-router     → News, crypto, stocks, songs, Wikipedia
  ├── jarvis-whatsapp   → Twilio WhatsApp send
  └── jarvis-email      → Gmail send
```

---

## ⚙️ Configuration

### Environment Variables

Copy `local-agent/.env.example` to `local-agent/.env` and configure:

```bash
# Chrome path
JARVIS_CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe

# n8n Router (required for internet research)
JARVIS_N8N_ROUTER_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-router

# Optional: WhatsApp auto-send via Twilio
JARVIS_WHATSAPP_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-whatsapp

# Optional: Email auto-send via Gmail
JARVIS_EMAIL_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-email

# Optional: OpenAI fallback (if n8n is offline)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

---

## 📱 WhatsApp Auto-Send Setup (Optional)

To enable real WhatsApp sending (not just drafts):

1. Sign up at [twilio.com](https://www.twilio.com)
2. Get a WhatsApp sandbox number
3. In n8n → **Settings → Environment Variables**, add:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```
4. Import and activate `n8n/jarvis-whatsapp.workflow.json`
5. Set `JARVIS_WHATSAPP_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-whatsapp` in `.env`

---

## 📧 Gmail Auto-Send Setup (Optional)

To enable real email sending (not just drafts):

1. In n8n → **Credentials → New → Gmail OAuth2**
2. Connect your Google account
3. Import and activate `n8n/jarvis-email.workflow.json`
4. Set `JARVIS_EMAIL_WEBHOOK_URL=http://localhost:5678/webhook/jarvis-email` in `.env`

---

## 🎙️ Voice Input

- Click **🎙 Voice** button in the UI
- Allow microphone permission in Chrome
- Select your language from the dropdown (English / Urdu / Hindi / Arabic)
- Speak your command
- JarvisX responds with both text and voice output

---

## 📁 Project Structure

```
JarvisX/
├── local-agent/           # FastAPI backend
│   ├── api/              # API routes
│   ├── core/             # Planner, executor, registry
│   ├── tools/            # Tool implementations
│   ├── app.py            # Main FastAPI app
│   ├── config.py         # Settings & env loader
│   └── .env.example      # Environment template
├── frontend/             # Voice UI
│   └── index.html        # Single-page app
├── n8n/                  # n8n workflow definitions
│   ├── jarvis-router.workflow.json
│   ├── jarvis-whatsapp.workflow.json
│   └── jarvis-email.workflow.json
├── docker/               # n8n Docker setup
│   ├── docker-compose.yml
│   └── .env              # n8n credentials
└── README.md             # This file
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** Vanilla HTML/CSS/JS with Web Speech API
- **Automation:** n8n (self-hosted via Docker)
- **APIs:** CoinGecko, Yahoo Finance, Google News RSS, Apple Music, Wikipedia, OpenWeatherMap
- **Communication:** Twilio WhatsApp API, Gmail OAuth2

---

## 📝 License

MIT License — feel free to use, modify, and distribute.

---

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

---

## 👤 Author

**Waleed** — [waleed671](https://github.com/waleed671)

Email: abrothers852@gmail.com

---

**Happy automating with JarvisX! 🚀**
