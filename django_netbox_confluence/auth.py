from django.http.response import JsonResponse
from django.conf import settings


def authentication_required(method):
    """
    Wrapper over view method/action like `post` or `get`.
    Checks whether client provided appropriate authentication header(token in Authorization header).

    :rtype: function
    :return: Wrapped function/decorator.
    """
    def wrapper(self, request):
        try:
            token = settings.DNC_WEBHOOK_TOKEN
        except AttributeError:
            return JsonResponse({
                "message": "DNC_WEBHOOK_TOKEN not set.",
                "error": "DNC_WEBHOOK_TOKEN not set.",
            }, status=401)

        if request.META.get('HTTP_AUTHORIZATION', None) != "Token {}".format(token):
            return JsonResponse({
                "message": "Unauthorized access.",
                "error": "Wrong atuthorization token. Please check your NetBox admin settings `Additional headers:`.",
            }, status=401)
        return method(self, request)

    return wrapper
