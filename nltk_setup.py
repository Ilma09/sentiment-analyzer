"""Run once at build/deploy time to make sure NLTK data is present."""
import nltk

for pkg in ("vader_lexicon", "punkt", "punkt_tab", "stopwords"):
    nltk.download(pkg, quiet=True)

print("NLTK data ready.")
