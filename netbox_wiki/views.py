import json

from django.views import View
from django.http.response import JsonResponse

from netbox_wiki.updater.wiki_updater import WikiPageUpdater


class NetboxVikiAPIView(View):
    http_method_names = ['post']

    def serialize_data(self, request):
        return {
            'event': 'updated',
            'timestamp': '2019-12-12 06:28:14.697248',
            'model': 'site',
            'username': 'hovhannes',
            'request_id': '05fd06f4-8825-4bb4-acb4-119f1ec7da04',
            'data': {
                'id': 1,
                'name': 'Office 1',
                'slug': 'office-1',
                'status': {
                    'value': 1,
                    'label': 'Active15'
                },
                'region': None,
                'tenant': None,
                'facility': '',
                'asn': 554,
                'time_zone': 'Asia/Yerevan',
                'description': 'Something',
                'physical_address': '40.1753932, 44.510232599999995',
                'shipping_address': 'Degheyan st',
                'latitude': '40.175393',
                'longitude': '44.510232',
                'contact_name': 'Hovhannes',
                'contact_phone': '1214514361',
                'contact_email': 'asdfj@dflskjg.com',
                'comments': 'Some comment for testing purposes.',
                'tags': ['testing', 'new'],
                'custom_fields': {
                    'purpose': 'Cepheus 15.'
                },
                'created': '2019-12-11',
                'last_updated': '2019-12-12T06:28:14.608353Z'
            }
        }
        return json.loads(request.body)


class SiteChangeTriggerView(NetboxVikiAPIView):
    def post(self, request):
        # Take data form Netbox webhook payload.
        data = self.serialize_data(request)

        # TODO: Handle in queue.
        # TODO: Update appropriate page with changed fields.
        WikiPageUpdater(data).update()

        return JsonResponse({
            "message": "Successfully updated.",
            "error": None,
        }, status=201)
