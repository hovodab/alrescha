`NetBox -> Confluence Wiki` Connector
=====================================

`django-netbox-confluence` is a synchronization tool which helps synchronize data described on the NetBox and appropriate pages on
Confluence Wiki.
When some page is edited on the NetBox the webhook is fired and calls the `django-netbox-confluence` endpoint which gathers the data
 and updates specific page for updated model on the Wiki. For each field/input it creates MultiExcerpt macro
  which then can be used in other pages providing "dynamic" content.

`django-netbox-confluence` uses NetBox webhooks in order to get information about changes and update the data on the Wiki.
For that purpose it is needed to create webhook on the NetBox admin.

`django-netbox-confluence` runs as a web application atop the [Django](https://www.djangoproject.com/)
For a complete list of requirements, see `requirements.txt`. The code is available [on GitHub](https://github.com/hovodab/alrescha).


### Prerequisites
- You should have NetBox running.
- You should have Confluence up and running.
- You should have MultiExcerpt macro plugin for Confluence installed.

> ##### *NOTE: Don't forget to run NetBox rqworker.*


## Installation
```bash
$ pip install django-netbox-confluence
```

## Configuration
Add app to INSTALLED_APPS list in the end of your Django settings file.
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'django_netbox_confluence',
]
```

Add confluence credentials settings and space key where the data will be stored variables in your Django settings file.
```python
DNC_CONFLUENCE_CREDENTIALS = {
    'url': 'http://localhost:8090',
    'username': 'admin',
    'password': 'admin'
}

DNC_SPACE_KEY = 'NETBOX'
```
> ##### *NOTE: If the space doesn't exist it will be created automatically when the first webhook fires.*

Add urls configuration in your urls.py.
```python
from django.urls import incluede, path


urlpatterns = [
    path('netbox-wiki-api/', include('django_netbox_confluence.urls')),
    ...
]
```


**Configure NetBox webhook.**
![Alt text](deploy/docs/netbox_config.png?raw=true "Optional Title")

- Choose appropriate `Object types` for the models/pages that you want to be synchronized with Confluence Wiki.
- Tick `Type create` or/and `Type update` when you want the synchronization to happen. Typically you should tick both.
- Fill `URL:` field with the endpoint where django_netbox_confluence runs. Example: `http://localhost:5000/netbox-wiki-api/model_change_trigger/`
- Don't forget to tick the `Enable` checkbox to enable the webhook.


### Add new field types.
If fields types that exist in admin dropdown are not enough, you can create your own fields.

Create a file where you will define new field type classes. Those classes should be derived from `AbstractLinkedField`.
Override `provide_value` method.

```python
from django_netbox_confluence.updater.linked_fields import AbstractLinkedField


class ObjectLinkedField(AbstractLinkedField):

    def provide_value(self):
        return self.value['id']

```

Add configuration in your settings file so the module could find file types defined by you.
```python
DNC_FIELD_TYPES_MODULES = [
    "my_app.my_linked_fields",
]
```

Migrate changes so the new fields appears in Django admin form.
```bash
$ python manage.py makemigratoins
$ python manage.py migrate
```