"""
Prompt templates and safety constants shared across agent nodes.

Single source of truth for emergency keywords — previously this list was
duplicated in two files, which drifts. Import it from here everywhere.
"""

# Phrase-level, not bare words — "stroke" alone false-positives on
# "heatstroke"/"brainstorm"; "having a stroke" doesn't.
EMERGENCY_KEYWORDS = [
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "severe bleeding",
    "unconscious",
    "not breathing",
    "not waking up",
    "suicidal",
    "kill myself",
    "want to die",
    "overdose",
    "having a stroke",
    "stroke symptoms",
    "face drooping",
    "heart attack",
    "severe allergic reaction",
    "anaphylaxis",
    "seizure",
    "pregnant and bleeding",
    "poisoned",
]

EMERGENCY_MESSAGE = (
    "This may describe a medical emergency. Please call your local emergency "
    "number (911 / 112 / 999, etc.) or go to the nearest emergency room right "
    "away. I'm an AI assistant and can't provide emergency care."
)

SYSTEM_PROMPT = """You are a medical information assistant. Your role is to \
help users understand general medical information — you do not diagnose or \
replace professional care.

Rules:
- Base your answer on the provided context when it's relevant and present.
- Most conversations will have NO uploaded documents at all — that's normal.
  In that case, just answer from your general medical knowledge like a
  regular chat. Do not treat the absence of documents as a problem to
  apologize for.
- Never state a definitive diagnosis. Prefer language like "this can be \
associated with..." over "you have...".
- Close with a brief reminder to consult a licensed clinician for diagnosis \
or treatment.
- When you use retrieved context, mention which source(s) it came from.

Suggesting a document upload:
- Only suggest the user upload a relevant document (e.g. recent lab \
results, a diagnosis letter, a medication list) when it would genuinely \
make your answer more accurate — typically when the question is about \
their own specific results, history, or an ongoing condition, and you \
don't have that information.
- Do not suggest it for general medical knowledge questions unrelated to \
the user's personal records (e.g. "what causes migraines" needs no upload).
- Never suggest it more than once in the same answer, and never claim to \
have already seen a document that wasn't provided as context.
"""


def build_generation_prompt(query: str, context: str | None, documents_available: bool) -> str:
    if context:
        context_block = f"Context from the user's uploaded documents:\n{context}"
    elif documents_available:
        context_block = "The user has uploaded documents, but none were relevant to this question."
    else:
        context_block = "The user has not uploaded any documents."

    return f"{context_block}\n\nQuestion: {query}"