import json

from django.conf import settings
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from django_netbox_confluence.updater.wiki_updater import WikiPageUpdater, WikiUpdateException
from django_netbox_confluence.auth import authentication_required


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

        assert "custom_fields" in data["data"], "No `custom_fields` in webhook payload data."
        assert type(data["data"]["custom_fields"]) is dict, ("`custom_fields` should be dict, got {}"
                                                             .format(type(data["data"]["custom_fields"])))


class ModelChangeTriggerView(NetBoxVikiAPIView):
    """
    Webhook handler.
    """

    @authentication_required
    def post(self, request):
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
