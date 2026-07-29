# Signal — Real-Time Sentiment Analyzer

A Flask REST API that classifies text as **Positive**, **Negative**, or **Neutral** in real time using
NLTK's **VADER** (Valence Aware Dictionary and sEntiment Reasoner), with NLP preprocessing
(tokenization + stopword removal) and a responsive HTML/CSS/JS frontend.

## Tech stack
- **Backend:** Python, Flask, REST API
- **NLP:** NLTK (VADER sentiment lexicon, `word_tokenize`, stopword removal)
- **Frontend:** HTML5, CSS3, vanilla JavaScript (no build step)
- **Deployment-ready for:** Render, Railway, PythonAnywhere, Heroku, or any WSGI host

## Project structure
```
sentiment-analyzer/
├── app.py                # Flask app + VADER sentiment logic + REST endpoints
├── nltk_setup.py         # One-time download of NLTK data (run at build time)
├── requirements.txt      # Python dependencies
├── Procfile              # Process definition for Render/Heroku
├── render.yaml            # One-click Render blueprint config
├── templates/
│   └── index.html        # Frontend page
└── static/
    ├── css/style.css      # Styling
    └── js/script.js       # Calls the REST API and renders results
```

## API endpoints

| Method | Route                | Body                                | Description                        |
|--------|-----------------------|--------------------------------------|-------------------------------------|
| GET    | `/`                   | —                                     | Serves the frontend                 |
| GET    | `/api/health`         | —                                     | Health check                        |
| POST   | `/api/analyze`        | `{"text": "..."}`                    | Analyze a single piece of text      |
| POST   | `/api/analyze-batch`  | `{"texts": ["...", "..."]}` (max 50) | Analyze multiple texts at once      |

Example:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I absolutely loved this!"}'
```
Response:
```json
{
  "sentiment": "Positive",
  "scores": {"positive": 0.643, "neutral": 0.357, "negative": 0.0, "compound": 0.6696},
  "keywords": ["absolutely", "loved"],
  "token_count": 6
}
```

## Run it locally

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data (one-time)
python nltk_setup.py

# 4. Run the app
python app.py
```
Then open **http://localhost:5000** in your browser.

---

## Deploy it live (free options)

### Option A — Render.com (recommended, easiest, free tier)

1. Push this project to a **GitHub repository**.
2. Go to [render.com](https://render.com) → sign up / log in → **New +** → **Web Service**.
3. Connect your GitHub repo.
4. Render will detect `render.yaml` automatically. If it doesn't, set manually:
   - **Build Command:** `pip install -r requirements.txt && python nltk_setup.py`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3
5. Click **Create Web Service**. Render builds and deploys automatically.
6. You'll get a live URL like `https://sentiment-analyzer-xxxx.onrender.com` — share this link.

> Free tier note: the service may "sleep" after 15 minutes of inactivity and take ~30–50 seconds to
> wake up on the next request. This is normal for free hosting tiers and fine for a demo/showcase link.

### Option B — Railway.app

1. Push the project to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Railway auto-detects Python. Add these settings if prompted:
   - **Build Command:** `pip install -r requirements.txt && python nltk_setup.py`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Deploy — Railway gives you a public `*.up.railway.app` URL.

### Option C — PythonAnywhere (no credit card, good for quick demos)

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Upload the project (via the **Files** tab or `git clone` in a Bash console).
3. In a Bash console: `pip install --user -r requirements.txt && python nltk_setup.py`
4. Go to the **Web** tab → **Add a new web app** → **Flask** → point it at `app.py`.
5. Reload the web app — your live link will be `https://yourusername.pythonanywhere.com`.

### Option D — Docker (any cloud provider)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python nltk_setup.py
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```
Build & run:
```bash
docker build -t sentiment-analyzer .
docker run -p 5000:5000 sentiment-analyzer
```

---

## How the NLP pipeline works

1. **Clean** — strip URLs/HTML/extra whitespace while keeping punctuation and case, since VADER uses
   those signals (e.g. `"great!!"` scores stronger than `"great"`, `"GREAT"` stronger than `"great"`).
2. **Tokenize** — `nltk.word_tokenize` splits the text into word/punctuation tokens.
3. **Stopword removal** — common words (`the`, `is`, `and`, …) are filtered out to surface the
   keywords that actually carry sentiment, shown in the UI for transparency.
4. **Score** — VADER's `SentimentIntensityAnalyzer` returns `pos`, `neu`, `neg`, and a normalized
   `compound` score; the compound score is thresholded (`>= 0.05` → Positive, `<= -0.05` → Negative,
   else Neutral) to produce the final label.

## Resume / portfolio blurb

> **Sentiment Analyzer** — Python, NLTK, Flask, REST API, HTML/CSS
> Built a Flask-based REST API using Python and NLTK/VADER to classify text as Positive, Negative, or
> Neutral in real time. Applied NLP preprocessing (tokenization, stopword removal) to surface
> sentiment-bearing keywords, and built a responsive HTML/CSS frontend for real-time interaction.
> Deployed live on Render.
