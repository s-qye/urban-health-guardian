import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    print(f"  Retry {attempt + 1}/{max_retries} in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator