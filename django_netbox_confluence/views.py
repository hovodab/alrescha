import json

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from django_netbox_confluence.updater.wiki_updater import WikiPageUpdater, WikiUpdateException


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
        """
        return json.loads(request.body)

    def validate_data(self, data):
        """
        Validating whether webhook body is formed right.
        """
        assert "model" in data, "No `model` in webhook payload."
        assert type(data["model"]) is str, "`model` should be string, got {}".format(type(data["model"]))

        assert "data" in data, "No `data` in webhook payload."
        assert type(data["data"]) is dict, "`data` should be dict, got {}".format(type(data["data"]))

        assert "custom_fields" in data["data"], "No `cusom_fields` in webhook payload data."
        assert type(data["data"]["custom_fields"]) is dict, ("`custom_fields` should be dict, got {}"
                                                             .format(type(data["data"]["custom_fields"])))


class ModelChangeTriggerView(NetBoxVikiAPIView):
    """
    Webhook handler.
    """
    def post(self, request):
        # Take data form NetBox webhook payload.
        data = self.serialize_data(request)
        self.validate_data(data)

        # TODO: Handle in queue.
        try:
            WikiPageUpdater(data).update()
        except WikiPageUpdater as e:
            return JsonResponse({
                "message": "Update failed.",
                "error": e,
            }, status=400)

        return JsonResponse({
            "message": "Successfully updated.",
            "error": None,
        }, status=201)
