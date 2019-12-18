========================
django_netbox_confluence
========================

Django-NetBox-Confluence is a Django app to connect NetBox and Confluence wiki. Define .

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "Django-NetBox-Confluence" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        'django_netbox_confluence',
    ]

2. Include the netbox-wiki URLconf in your project urls.py like this::

    path('netbox-wiki-api/', include('django_netbox_confluence.urls'))


3. Add confluence credentials settings and space key where the data will be stored variables in your Django settings file.

    DNC_CONFLUENCE_CREDENTIALS = {
        'url': 'http://localhost:8090',
        'username': 'admin',
        'password': 'admin'

    }

    DNC_SPACE_KEY = 'NETBOX'

    DNC_WEBHOOK_TOKEN = "<SECRET_KEY>"

4. Run `python manage.py migrate` to create the Django-NetBox-Confluence models.

5. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a configuration (you'll need the Admin app enabled). Set authorization header: {"Authorization": "Token <SECRET_KEY>"}.

6. Use http://127.0.0.1:8000/netbox-wiki/model_change_trigger as NetBox webhook endpoint URL field input.
