from tavily import TavilyClient
from app.medical_agent.core.config import settings

_client = None

def get_tavily_client():
    global _client
    if _client is None:
        _client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    return _client

def search_web(query: str, max_results: int = 3) -> list[dict]:
    """Return list of {title, url, content} from web search."""
    if not settings.TAVILY_API_KEY:
        return []
    client = get_tavily_client()
    response = client.search(query=query, max_results=max_results, search_depth="basic")
    results = []
    for res in response.get("results", []):
        results.append({
            "title": res.get("title", ""),
            "url": res.get("url", ""),
            "content": res.get("content", ""),
        })
    return results