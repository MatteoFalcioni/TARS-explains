# TARS-explains

**TARS-explains** is a voice-driven physics explainer powered by a LangGraph agent ("TARS" - inspired by the *Interstellar* robot), OpenAI Whisper for speech-to-text (STT), and ElevenLabs for text-to-speech (TTS). 

Users speak; the system transcribes, generates an answer, and synthesizes audio in a TARS-like voice.

If asked about physics or mathematics questions, the system also provides supporting equations as Markdown files rendered in chat.

A React frontend provides a clean interface with push‑to‑record, chat history, audio playback, and rendered equations with global numbering `(eq. n)`.

---

## Features

* **Push‑to‑talk** recording in the browser (toggle to start/stop).
* **LangGraph agent** answering as TARS (humor controlled via voice, not UI).
* **Equations to files**: written as Markdown into `/equations` (cleared each run) and rendered in the UI via KaTeX.
* **Audio reply** via ElevenLabs; served as MP3 and auto‑played in the chat.
* **Chat history** UI (User / TARS bubbles) with progressive equation numbering across the session.

---

## Architecture

**Backend (FastAPI + LangGraph)**

* `POST /api/ask` — accepts uploaded audio (from the browser), runs: Whisper → TARS (LangGraph) → ElevenLabs; writes equations as Markdown and returns JSON.
* Static file serving: `/equations/*` (equation Markdown) and `/outputs/*` (synthesized MP3).
* `GET /health` for readiness.

**Frontend (Vite + React + TailwindCSS)**

* Toggle mic button using the Web `MediaRecorder` API.
* Sends the recorded blob to `/api/ask`.
* Renders transcript (User), TARS text + audio, and equations (KaTeX), numbering `(eq. 1), (eq. 2), …` across the chat.

**Agent (LangGraph)**

* REACT agent with tools:

  * `write_equations(content)` → writes one Markdown equation file.
  * `get_humor()` / `set_humor(value)`.
* Prompt enforces: equations are written to files, not embedded in the reply text; references appear as text (e.g., “(equation 1)”).

> A diagram of the parent/subgraph is available in `./tars_graph.png` (generated from your LangGraph definition).

---

## Repository Layout (high level)

```
TARS-explains/
├── deploy/
│ └── nginx.conf
├── api_app.py # FastAPI server (/api/ask, /equations, /outputs, /health)
├── T2S_S2T/
│ ├── text_2_speech.py  # Eleven-Labs for text to speech
│ └── speech_2_text.py  # Whisper for speech to text
├── TARS/
│ ├── graph.py # LangGraph build + TARS node
│ ├── prompt.py # TARS prompt rules
│ ├── state.py # Agent state & reducers (humor, equations)
│ └── tools.py # write_equations / get_humor / set_humor
├── equations/ # generated per run (cleared at /api/ask start)
├── outputs/ # synthesized MP3 replies
├── tars_graph.png # LangGraph visualization (optional)
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.web
├── requirements.txt
├── LICENSE
└── frontend/tars-frontend # React app (Vite + TailwindCSS)

```

---

## Prerequisites

* **Python** ≥ 3.11
* **Node.js** ≥ 18 (recommended 20)
* **OpenAI API key** (Whisper STT)
* **ElevenLabs API key** (TTS)
* (Optional) **Docker** + **Docker Compose v2** for containerized runs

---

## Quick Start With Docker (*recommended*) 

This setup serves the built React app via Nginx and proxies API/static routes to the FastAPI container, so the browser uses a single origin (no CORS).

Put the required environment variables inside your `.env.api`, following the template `.env.template`.

Then simply run from the root directory

```bash
docker compose build
docker compose up
```

You will find the app running at **[http://localhost:8080](http://localhost:8080)**.

> **Flow**: Click **Record**, then **Stop** → the browser POSTs audio to `/api/ask`; the backend clears `equations/`, transcribes with Whisper, runs TARS, synthesizes MP3 with ElevenLabs, returns JSON. The frontend shows the transcript (“User:”), the explanation (“TARS:”), auto‑plays the MP3, and renders all equations with global numbering.

---

## Quick Start (Local, without Docker - *not recommended*)

### 1) Backend — FastAPI

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (your preferred method):

   * Create a `.env` (or use `.env.api`) with:

     ```bash
     OPENAI_API_KEY=sk-...
     XI_API_KEY=elevenlabs_...
     ```

3. Run the API:

   ```bash
   uvicorn api_app:app --reload
   ```

   * Health: [http://localhost:8000/health](http://localhost:8000/health) → `{ "status": "ok" }`
   * Static: [http://localhost:8000/equations/](http://localhost:8000/equations/) and [http://localhost:8000/outputs/](http://localhost:8000/outputs/)

### 2) Frontend — React (Vite)

1. Install dependencies:

   ```bash
   cd tars-frontend
   npm install
   ```

2. (Tailwind v3.4) Ensure `tailwind.config.js` includes:

   ```js
   export default {
     content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
     theme: { extend: { keyframes: { /* custom glow/ripple if used */ }, animation: {} } },
     plugins: [],
   }
   ```

   and `src/index.css`:

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;

   body { @apply bg-gray-900 text-gray-100 font-mono; }
   ```

3. Start the dev server:

   ```bash
   npm run dev
   ```

   Open [http://localhost:5173](http://localhost:5173) and use the **Record** toggle. By default the frontend talks to `http://localhost:8000` (absolute) or to relative `/api/*` if you configured an Nginx proxy as in the Docker setup below.

---

## API Contract

**POST** `/api/ask`

* Body: `multipart/form-data` with `audio` (webm/wav/mp3)
* Response: `200 OK`

  ```json
  {
    "transcript": "Your spoken question…",
    "text": "TARS explanation…",
    "audio_url": "/outputs/response_abc123.mp3",
    "equations": [
      { "filename": "equations/equation_1a2b3c.md", "content": "# Equation 1\n\n$$E=mc^2$$" }
    ]
  }
  ```

**GET** `/equations/*` and `/outputs/*` serve static files.

**GET** `/health` → `{ "status": "ok" }`.

---

## Roadmap (next iterations)

* Wake‑word activation ("Hey TARS") and VAD in the browser.
* Session history & export (equations bundle, audio transcript).
* Server‑side session persistence (DB) and per‑user global equation counters.
* Theming & accessibility polish; mobile layout tweaks.

---

## License

add license
