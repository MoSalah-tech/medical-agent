"""
Speech-to-text via Groq Whisper.

The Groq SDK call is blocking network I/O. `transcribe_audio` wraps it in
`run_in_threadpool` so it never blocks the FastAPI event loop when called
from an async route or an async LangGraph node.
"""

from typing import Optional

import groq
from starlette.concurrency import run_in_threadpool

from medical_agent.core.config import settings

_client: Optional[groq.Groq] = None


class STTError(Exception):
    pass


def _get_client() -> groq.Groq:
    global _client
    if _client is None:
        _client = groq.Groq(api_key=settings.GROQ_API_KEY)
    return _client


def _transcribe_sync(audio_file_path: str) -> str:
    client = _get_client()
    with open(audio_file_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model=settings.GROQ_STT_MODEL,
            file=f,
            response_format="text",
        )
    # response_format="text" returns a plain string in groq-python today;
    # guard in case a future SDK version wraps it in an object instead.
    return result if isinstance(result, str) else getattr(result, "text", str(result))


async def transcribe_audio(audio_file_path: str) -> str:
    try:
        return await run_in_threadpool(_transcribe_sync, audio_file_path)
    except FileNotFoundError as exc:
        raise STTError(f"Audio file not found: {audio_file_path}") from exc
    except Exception as exc:
        raise STTError(f"Transcription failed: {exc}") from exc