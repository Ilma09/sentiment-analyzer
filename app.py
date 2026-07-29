"""
Sentiment Analyzer - Flask REST API
------------------------------------
Uses NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) to classify
text as Positive, Negative, or Neutral in real time.

Applies NLP preprocessing (tokenization, stopword removal, cleaning) to surface
the meaningful keywords driving each prediction, and serves a small REST API
consumed by the bundled HTML/CSS/JS frontend.
"""

import os
import re
import string

import nltk
from flask import Flask, jsonify, render_template, request
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize


# ---------------------------------------------------------------------------
# NLTK data bootstrap (safe to call every boot — no-ops if already present)
# ---------------------------------------------------------------------------
def ensure_nltk_data():
    required = {
        "vader_lexicon": "sentiment/vader_lexicon.zip",
        "punkt": "tokenizers/punkt",
        "punkt_tab": "tokenizers/punkt_tab",
        "stopwords": "corpora/stopwords",
    }
    for pkg, path in required.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


ensure_nltk_data()

STOP_WORDS = set(stopwords.words("english"))
analyzer = SentimentIntensityAnalyzer()

app = Flask(__name__)


# ---------------------------------------------------------------------------
# NLP preprocessing pipeline
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Strip URLs, HTML tags, and extra whitespace while preserving
    punctuation/case that VADER relies on (e.g. '!', 'GREAT')."""
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_filter(text: str):
    """Tokenize and remove stopwords/punctuation — used to extract the
    keywords that actually carry sentiment, for display/insight purposes."""
    tokens = word_tokenize(text.lower())
    keywords = [
        t for t in tokens
        if t not in STOP_WORDS and t not in string.punctuation and t.isalpha()
    ]
    return tokens, keywords


def classify(compound: float) -> str:
    """Standard VADER thresholds."""
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def analyze_text(raw_text: str) -> dict:
    cleaned = clean_text(raw_text)
    tokens, keywords = tokenize_and_filter(cleaned)

    # VADER is lexicon + rule based and is designed to score raw text
    # (it understands negation, punctuation emphasis, capitalization, and
    # emoji/slang) so we score the cleaned-but-unstripped text for accuracy,
    # while still surfacing the stopword-filtered keywords for transparency.
    scores = analyzer.polarity_scores(cleaned)
    sentiment = classify(scores["compound"])

    return {
        "original_text": raw_text,
        "cleaned_text": cleaned,
        "sentiment": sentiment,
        "scores": {
            "positive": round(scores["pos"], 3),
            "negative": round(scores["neg"], 3),
            "neutral": round(scores["neu"], 3),
            "compound": round(scores["compound"], 3),
        },
        "token_count": len(tokens),
        "keywords": keywords[:15],  # top keywords after stopword removal
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please provide non-empty 'text' in the request body."}), 400

    if len(text) > 5000:
        return jsonify({"error": "Text is too long (max 5000 characters)."}), 400

    result = analyze_text(text)
    return jsonify(result), 200


@app.route("/api/analyze-batch", methods=["POST"])
def analyze_batch():
    data = request.get_json(silent=True) or {}
    texts = data.get("texts")

    if not isinstance(texts, list) or not texts:
        return jsonify({"error": "Please provide a non-empty 'texts' list."}), 400
    if len(texts) > 50:
        return jsonify({"error": "Max 50 items per batch request."}), 400

    results = [analyze_text(str(t)) for t in texts if str(t).strip()]
    return jsonify({"results": results, "count": len(results)}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
