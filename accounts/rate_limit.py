from functools import wraps

from django.core.cache import cache
from django.http import JsonResponse, HttpResponse


def _client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def rate_limit(key_prefix, limit, window_seconds, methods=('POST',), by_user=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.method not in methods:
                return view_func(request, *args, **kwargs)

            scope = request.user.pk if by_user and getattr(request.user, 'is_authenticated', False) else _client_ip(request)
            cache_key = f'rate-limit:{key_prefix}:{scope}'
            current = cache.get(cache_key, 0)

            if current >= limit:
                payload = {'success': False, 'error': 'Trop de requetes. Reessayez plus tard.'}
                if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/accounts/api/'):
                    return JsonResponse(payload, status=429)
                return HttpResponse(payload['error'], status=429)

            cache.set(cache_key, current + 1, timeout=window_seconds)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
