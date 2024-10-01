from django.http import HttpResponseForbidden

BLOCKED_IPS = ["172.16.139.218"]
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5 (Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot)"
]


class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")
        if ip_address in BLOCKED_IPS and user_agent in USER_AGENTS:
            return HttpResponseForbidden("Access Denied")
        return self.get_response(request)
