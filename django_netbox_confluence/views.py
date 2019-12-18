import json

from django.conf import settings
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from django_netbox_confluence.updater.wiki_updater import WikiPageUpdater, WikiUpdateException
from django_netbox_confluence.updater.exceptioins import AuthorizationException


class NetBoxVikiAPIView(View):
    """
    Base for all NetBox webhook handlers.
    """
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def serialize_data(self, request):
        """
        Get data serialized as dict.

        :type request: WSGIRequest
        :param request: Request object.

        :rtype: dict
        :return: Serialized request body.
        """
        return json.loads(request.body)

    def validate_data(self, data):
        """
        Validating whether webhook body is formed right.

        :type data: dict
        :param data: Webhook body.

        :rtype: void
        :returns: void
        """
        assert "model" in data, "No `model` in webhook payload."
        assert type(data["model"]) is str, "`model` should be string, got {}".format(type(data["model"]))

        assert "data" in data, "No `data` in webhook payload."
        assert type(data["data"]) is dict, "`data` should be dict, got {}".format(type(data["data"]))

        assert "custom_fields" in data["data"], "No `cusom_fields` in webhook payload data."
        assert type(data["data"]["custom_fields"]) is dict, ("`custom_fields` should be dict, got {}"
                                                             .format(type(data["data"]["custom_fields"])))

    def check_token(self, request):
        """
        Check whether authorization token is correctly provided or not.

        :raises: WikiUpdateException
        :raises: AuthorizationException

        :rtype: void
        :return: void
        """
        try:
            token = settings.DNC_WEBHOOK_TOKEN
        except AttributeError:
            raise WikiUpdateException("Can't find `DNC_WEBHOOK_TOKEN` in settings file. Please check. ")

        if request.META.get('HTTP_AUTHORIZATION', None) != "Token {}".format(settings.DNC_WEBHOOK_TOKEN):
            raise AuthorizationException("Wrong authorizatoin token."
                                         " Please check your Netbox admin settings `Additional headers:`.")


class ModelChangeTriggerView(NetBoxVikiAPIView):
    """
    Webhook handler.
    """
    def post(self, request):
        # TODO: Change authentication system.
        try:
            self.check_token(request)
        except (AuthorizationException, WikiUpdateException) as e:
            return JsonResponse({
                "message": "Unauthorized access.",
                "error": str(e),
            }, status=401)

        # Take data form NetBox webhook payload and validate format.
        try:
            data = self.serialize_data(request)
            self.validate_data(data)
        except (json.JSONDecodeError, AssertionError) as e:
            return JsonResponse({
                "message": "Invalid input.",
                "error": str(e),
            }, status=400)

        # TODO: Handle in queue.
        try:
            WikiPageUpdater(data).update()
        except WikiUpdateException as e:
            return JsonResponse({
                "message": "Update failed.",
                "error": str(e),
            }, status=400)

        return JsonResponse({
            "message": "Successfully updated.",
            "error": None,
        }, status=201)
