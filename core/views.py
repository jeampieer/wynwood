from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})


def ping(request):
    return JsonResponse({"status": "ok", "message": "pong"})
