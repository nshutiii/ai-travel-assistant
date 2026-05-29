import re
from typing import Optional
from duckduckgo_search import DDGS

PRICE_RE = re.compile(r"(?:\$|USD|€|EUR|£|GBP)\s?([0-9]+(?:\.[0-9]{1,2})?)")


def search_affordable_airfare(origin: str, destination: str, outbound_date: str | None = None) -> Optional[float]:
    """Attempt a lightweight DuckDuckGo search for indicative cheap flight prices between origin and destination.

    Returns the lowest price found as float (USD approximate) or None if nothing found.
    This is best-effort and intended to provide an estimate, not a booking-grade quote.
    """
    query = f"cheap flights {origin} to {destination} cheapest price"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, safesearch='Off', timelimit=5)
            # results is an iterator of dicts with 'text' fields; collect small sample
            snippets = []
            for i, r in enumerate(results):
                if i >= 12:
                    break
                txt = r.get('body') or r.get('text') or ''
                snippets.append(txt)

        candidates = []
        for s in snippets:
            for m in PRICE_RE.finditer(s):
                try:
                    candidates.append(float(m.group(1)))
                except Exception:
                    continue

        if not candidates:
            return None
        # Return the minimum found
        return min(candidates)
    except Exception:
        return None
