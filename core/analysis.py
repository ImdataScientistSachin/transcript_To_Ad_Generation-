"""Transcript analysis utilities.

Enhanced analysis using spaCy when available. The output schema is more
structured and deterministic:

- `keywords`: list of dicts: `{term: str, score: float}` sorted by score desc
- `entities`: list of dicts: `{text: str, label: str}`
- `pos`: mapping from POS tag -> count
- `highlights`: list of top sentences (up to 3)

If spaCy isn't available the function falls back to a deterministic
heuristic and logs a warning so users know enhanced extraction wasn't
used.
"""
from typing import Dict, List, Any
from utils_logging import get_logger

logger = get_logger(__name__)

_nlp = None


def _get_nlp():
    """Load and cache the spaCy nlp model if available.

    Returns None if spaCy or the model isn't available.
    """
    global _nlp
    if _nlp is not None:
        return _nlp
    try:
        import spacy

        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            # The model may not be installed in lightweight dev environments.
            # We surface a debug-level message and continue with a heuristic
            # fallback so the rest of the pipeline remains usable.
            logger.debug("Failed to load en_core_web_sm model: %s", e)
            _nlp = None
    except Exception as e:
        # spaCy package missing — keep running with heuristic analysis.
        logger.debug("spaCy not installed: %s", e)
        _nlp = None
    if _nlp is None:
        logger.warning("spaCy model `en_core_web_sm` not available — using heuristic analysis")
    return _nlp


def analyze_transcript(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """Produce structured insights from a transcript.

    The `keywords` array contains items with normalized frequency-based
    scores in [0,1]. POS breakdown and named entities are returned when
    spaCy is available.
    """
    text = (transcript.get("text") or "").strip()
    nlp = _get_nlp()

    keywords: List[Dict[str, object]] = []
    entities: List[Dict[str, str]] = []
    pos: Dict[str, int] = {}

    if not text:
        return {
            "keywords": [],
            "entities": [],
            "pos": {},
            "highlights": [],
            "duration_seconds": transcript.get("duration_seconds"),
        }

    if nlp:
        doc = nlp(text)
        # Build stopwords set (combine spaCy stop words and a small custom set)
        stopwords = (
            set(w.lower() for w in nlp.Defaults.stop_words)
            if hasattr(nlp, 'Defaults')
            else set()
        )
        stopwords |= {
            "product",
            "company",
            "customer",
            "week",
            "weeks",
            "guest",
            "source",
            "vibe",
            "transcript",
            "interview",
        }

        candidates: List[str] = []
        # Token-level filtering: we count POS frequency and pick candidate
        # lemmas for keywords. This keeps the keyword list focused on
        # content-bearing words (nouns, proper nouns, adjectives).
        for token in doc:
            pos[token.pos_] = pos.get(token.pos_, 0) + 1
            if token.is_stop or token.is_punct or token.like_num:
                continue
            # Favor nouns, proper nouns and adjectives for keywords
            if token.pos_ in {"NOUN", "PROPN", "ADJ"}:
                lemma = token.lemma_.lower().strip()
                if len(lemma) > 3 and lemma not in stopwords and lemma.isalpha():
                    candidates.append(lemma)

        # Frequency map
        freq: Dict[str, int] = {}
        for c in candidates:
            freq[c] = freq.get(c, 0) + 1

        if freq:
            max_count = max(freq.values())
            # produce list of dicts with normalized score
            kws = sorted(
                freq.items(), key=lambda kv: (-kv[1], candidates.index(kv[0]))
            )
            for term, count in kws[:8]:
                keywords.append({"term": term, "score": round(count / max_count, 3)})

        # Named entities (cleaned)
        # Named entities: surface the raw text and spaCy label. This is
        # useful for downstream UI displays (e.g., highlighting people,
        # organizations, locations) and for ad creative signals.
        for ent in doc.ents:
            # filter out very short or punctuation-only ents
            text_ent = ent.text.strip()
            if len(text_ent) > 1:
                entities.append({"text": text_ent, "label": ent.label_})

        # Highlights: prefer concise sentence that contains a top candidate
        # Highlights: prefer a concise sentence that contains a top
        # candidate keyword. This often produces a short punchy line that
        # works well as ad copy or a testimonial pull-quote.
        sents = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 20]
        best_sentence = ""
        if sents:
            # try to find a sentence containing any top candidate
            top_candidates = list(freq.keys()) if freq else []
            found = None
            for sent in sents:
                ls = sent.lower()
                for c in top_candidates[:5]:
                    if c in ls:
                        found = sent
                        break
                if found:
                    break
            if found:
                best_sentence = found
            else:
                # fallback: pick the shortest reasonable sentence (more punchy)
                best_sentence = min(sents, key=lambda s: len(s))
        highlights = [best_sentence] if best_sentence else (text.split("\n")[:3])
    else:
        # Heuristic fallback: when spaCy isn't available we compute a
        # simple frequency-based keyword list and return the first few
        # lines as highlights. This keeps the project usable in CI and
        # lightweight dev environments.
        stopwords = {
            "the",
            "and",
            "a",
            "an",
            "to",
            "of",
            "in",
            "is",
            "that",
            "this",
            "about",
            "you",
            "your",
        }
        stopwords |= {
            "product",
            "company",
            "customer",
            "guest",
            "source",
            "vibe",
            "transcript",
            "interview",
            "week",
            "weeks",
        }
        words = [w.strip(".,?!;:\"'()[]") for w in text.lower().split()]
        freq = {}
        for w in words:
            if w and w.isalpha() and w not in stopwords and len(w) > 3:
                freq[w] = freq.get(w, 0) + 1
        if freq:
            max_count = max(freq.values())
            kws = sorted(freq.items(), key=lambda kv: -kv[1])
            for term, count in kws[:8]:
                keywords.append({"term": term, "score": round(count / max_count, 3)})
        highlights = text.split("\n")[:3]

    return {
        "keywords": keywords,
        "entities": entities,
        "pos": pos,
        "highlights": highlights,
        "duration_seconds": transcript.get("duration_seconds"),
    }
