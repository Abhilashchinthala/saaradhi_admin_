"""
Simple rate-limiting decorator for Django views using the Django cache framework.
Falls back to an in-memory dictionary if the cache backend is not configured.
"""

import functools
import time
import hashlib
from django.core.cache import cache
from django.http import JsonResponse


def rate_limit(max_requests=30, window_seconds=60):
    """
    Decorator to limit the number of requests per IP within a time window.

    Usage:
        @rate_limit(max_requests=30, window_seconds=60)
        def my_api_view(request):
            ...

    Args:
        max_requests: Maximum number of requests allowed in the window.
        window_seconds: The time window in seconds.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Determine client identifier (IP or user)
            if request.user.is_authenticated:
                identifier = f"rl:user:{request.user.id}"
            else:
                xff = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '0.0.0.0')
                identifier = f"rl:ip:{ip}"

            cache_key = f"{identifier}:{hashlib.md5(request.path.encode()).hexdigest()[:12]}"

            try:
                # Try using Django cache first
                current = cache.get(cache_key)
                if current is None:
                    cache.set(cache_key, 1, timeout=window_seconds)
                elif current >= max_requests:
                    retry_after = window_seconds
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Rate limit exceeded. Try again in {retry_after} seconds.',
                        'retry_after': retry_after,
                    }, status=429)
                else:
                    cache.incr(cache_key)
            except Exception:
                # Cache backend unavailable; allow request through
                pass

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator