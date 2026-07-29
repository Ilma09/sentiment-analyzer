const textInput   = document.getElementById('text-input');
const charCount   = document.getElementById('char-count');
const analyzeBtn  = document.getElementById('analyze-btn');
const sampleBtn   = document.getElementById('sample-btn');
const resultBox   = document.getElementById('result');
const meterSection = document.getElementById('meter-section');
const needle      = document.getElementById('spectrum-needle');
const keywordsBox = document.getElementById('keywords');

const SAMPLES = [
  "The onboarding was confusing at first, but support fixed it fast — genuinely impressed.",
  "This is the worst update they've shipped. Nothing works and nobody responds to tickets.",
  "The package arrived on Tuesday and contained three items.",
  "Absolutely loved the workshop! Best three hours I've spent all year.",
  "I'm not sure how I feel about the redesign, honestly. Some parts are fine, others are annoying."
];

textInput.addEventListener('input', () => {
  charCount.textContent = textInput.value.length;
});

sampleBtn.addEventListener('click', () => {
  const pick = SAMPLES[Math.floor(Math.random() * SAMPLES.length)];
  textInput.value = pick;
  charCount.textContent = pick.length;
  textInput.focus();
});

textInput.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    analyze();
  }
});

analyzeBtn.addEventListener('click', analyze);

async function analyze() {
  const text = textInput.value.trim();
  if (!text) {
    renderError('Type something first — even a sentence or two works.');
    return;
  }

  setLoading(true);
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();

    if (!res.ok) {
      renderError(data.error || 'Something went wrong analyzing that text.');
      return;
    }
    renderResult(data);
  } catch (err) {
    renderError('Could not reach the API. Is the server running?');
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  analyzeBtn.textContent = isLoading ? 'Analyzing…' : 'Analyze text';
}

function renderError(message) {
  resultBox.classList.add('is-empty');
  resultBox.innerHTML = `<div class="result-error">⚠ ${escapeHtml(message)}</div>`;
  meterSection.style.display = 'none';
}

function renderResult(data) {
  resultBox.classList.remove('is-empty');
  const { sentiment, scores, keywords, token_count } = data;

  resultBox.innerHTML = `
    <div class="result-card">
      <span class="result-label label-${sentiment}">${sentiment}</span>
      <span class="result-meta">
        compound ${scores.compound.toFixed(3)} · ${token_count} tokens analyzed
      </span>
    </div>
  `;

  // Update spectrum needle: compound ranges -1..1 -> 0%..100%
  const pct = ((scores.compound + 1) / 2) * 100;
  needle.style.left = `${pct}%`;

  // Update bars
  updateBar('pos', scores.positive);
  updateBar('neu', scores.neutral);
  updateBar('neg', scores.negative);

  // Keywords
  keywordsBox.innerHTML = keywords.length
    ? keywords.map(k => `<span class="keyword-chip">${escapeHtml(k)}</span>`).join('')
    : '<span class="result-meta">No standalone keywords after filtering — mostly stopwords/punctuation.</span>';

  meterSection.style.display = 'block';
}

function updateBar(kind, value) {
  const fill = document.getElementById(`bar-${kind}`);
  const val  = document.getElementById(`val-${kind}`);
  fill.style.width = `${Math.round(value * 100)}%`;
  val.textContent = value.toFixed(2);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
