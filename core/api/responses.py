from rest_framework.response import Response


class ApiResponse:
    @staticmethod
    def success(data=None, message="", status=200, meta=None):
        payload = {
            "success": True,
            "message": message,
            "data": data,
        }
        if meta is not None:
            payload["meta"] = meta
        return Response(payload, status=status)
