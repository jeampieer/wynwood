class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.GET.get("lang")
        if language in {"es", "en"}:
            request.session["site_language"] = language
        return self.get_response(request)
