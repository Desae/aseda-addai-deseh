import json
from typing import Dict, Any, List, Optional
import requests
from urllib.parse import urlparse

from ..config import SERPER_API_KEY, SERPER_SEARCH_URL


class SerperError(Exception):
    pass


def serper_program_search(
    query: str,
    num_results: int = 20,
    country: Optional[str] = None,
    locale: str = "en",
) -> Dict[str, Any]:
    """
    Call Serper.dev to run a Google search.

    Args:
        query: Search query string.
        num_results: Approx number of organic results.
        country: Optional 2-letter country code, e.g. 'us', 'ca'.
        locale: Language code, e.g. "en".

    Returns:
        The raw JSON response from Serper.
    """
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "q": query,
        "num": num_results,
        "hl": locale,
    }
    if country:
        payload["gl"] = country

    resp = requests.post(SERPER_SEARCH_URL, headers=headers, data=json.dumps(payload), timeout=20)
    if resp.status_code != 200:
        raise SerperError(f"Serper API error {resp.status_code}: {resp.text}")
    
    result = resp.json()
    print(f"[DEBUG] Serper API response keys: {result.keys()}")
    if "organic" in result:
        print(f"[DEBUG] Number of organic results from Serper: {len(result.get('organic', []))}")
    
    return result


def extract_program_candidates(serper_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract structured candidate programs from a Serper JSON response.
    """
    organic = serper_json.get("organic", []) or []
    candidates: List[Dict[str, Any]] = []
    
    print(f"[DEBUG] Serper returned {len(organic)} organic results")

    for item in organic:
        title = item.get("title") or ""
        url = item.get("link") or ""
        snippet = item.get("snippet") or ""
        try:
            domain = urlparse(url).netloc
        except Exception:
            domain = ""

        candidates.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": domain,
            }
        )
    return candidates
