# YouTube Video Summariser

Paste any YouTube URL to get an AI-generated transcript summary. Optionally email the summary to yourself.

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) running locally with the following models pulled:
  - `llama3.1` — for summarisation
  - `nomic-embed-text` — for RAG embeddings

## Setup

### 1. Clone the repo

```bash
git clone <repo-url>
cd yt-podcast-summariser
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure email (optional)

Copy the `.env` file and fill in your SMTP credentials:

```bash
# Edit .env with your details
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-email@gmail.com
```

> **Gmail users:** Generate an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2-Step Verification). Use that instead of your account password.

### 4. Pull Ollama models

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Running the Web App

Start Ollama in one terminal:

```bash
ollama serve
```

Launch the Streamlit app in another:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage

1. Paste a YouTube URL (e.g. `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`)
2. Click **Summarise**
3. View the full transcript or read the AI summary
4. Enter your email address and click **Send to Email** to receive the summary

## Running the CLI (original)

```bash
python main.py
```

Follow the prompts to enter a YouTube URL and interact with the AI via the terminal.

## Project Structure

```
yt-podcast-summariser/
├── app.py           # Streamlit web app (entry point)
├── main.py          # Core logic: transcript fetch, summarisation, CLI
├── rag.py           # RAG: embeddings and similarity search
├── sqlite.py        # In-memory SQLite cache for summaries
├── requirements.txt # Python dependencies
└── .env             # SMTP credentials (not committed)
```

## Notes

- Summaries are cached in memory for the duration of the session. Submitting the same URL twice loads from cache instantly.
- Videos without captions/subtitles cannot be transcribed.
- Summarisation time depends on transcript length and local hardware (typically 30–120 seconds).
