import time
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from app.services.free_ai import generate_free_ai_itinerary
from app.services.ai_itinerary import generate_ai_itinerary
from app.services.smart_knowledge import generate_smart_itinerary


def _generate_uncached(destination: str, days: int, trip_style: str, budget: float, timeout: int = 12) -> List[Dict]:
    """Run multiple AI providers in parallel and return the first good response within timeout.

    If none return a usable result within the timeout, fall back to the local smart knowledge generator.
    """
    # Coerce budget to float to avoid Decimal * float TypeErrors from SQLAlchemy
    try:
        budget = float(budget)
    except Exception:
        budget = float(str(budget))

    providers = [generate_free_ai_itinerary, generate_ai_itinerary]

    with ThreadPoolExecutor(max_workers=len(providers)) as ex:
        futures = {ex.submit(p, destination, days, trip_style, budget): p for p in providers}

        start = time.time()
        try:
            for fut in as_completed(futures, timeout=timeout):
                try:
                    res = fut.result()
                except Exception:
                    # provider failed, continue waiting for others
                    continue

                # Basic validation: must be a non-empty list of day dicts
                if res and isinstance(res, list) and len(res) > 0:
                    return res
        except Exception:
            # timeout or other as_completed error
            pass

    # Final fallback: use the fast local knowledge generator
    return generate_smart_itinerary(destination, days, trip_style, budget)


@functools.lru_cache(maxsize=256)
def generate_itinerary_fast(destination: str, days: int, trip_style: str, budget: float, timeout: int = 12) -> List[Dict]:
    """Cached wrapper around the concurrent AI generation.

    Caching helps repeated requests for the same parameters return instantly.
    """
    # Ensure inputs are primitive types for stable caching keys
    try:
        budget_f = float(budget)
    except Exception:
        budget_f = float(str(budget))
    days_i = int(days)
    trip_style_s = str(trip_style).lower().strip() if trip_style else ""
    destination_s = str(destination).strip()

    return _generate_uncached(destination_s, days_i, trip_style_s, budget_f, timeout)
