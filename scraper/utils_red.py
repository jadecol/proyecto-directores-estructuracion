import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=2, max_delay=15):
    """
    Decorador para manejar Rate Limits (429) y Timeouts.
    Implementa Exponential Backoff con Jitter.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "timeout" in error_msg or "too many requests" in error_msg:
                        if attempt == max_retries - 1:
                            print(f"[!] Maximos reintentos alcanzados en {func.__name__}")
                            raise
                        
                        # Exponential backoff + jitter
                        sleep_time = min(max_delay, base_delay * (2 ** attempt)) + random.uniform(0.5, 2.0)
                        print(f"[*] Rate Limit/Timeout en {func.__name__}. Reintentando en {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                    else:
                        raise e
            return []
        return wrapper
    return decorator

def get_base_headers(auth_token=None, cookie_string=None):
    """Genera headers rotativos base para peticiones REST/GraphQL directas."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    if cookie_string:
        headers["Cookie"] = cookie_string
        
    return headers
