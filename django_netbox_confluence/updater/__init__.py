import importlib

from django.conf import settings


# Import fields defined by other apps in configured locations.
# TODO: may be it makes sense to import from apps specific locations and leave this way as alternative.
for elem in getattr(settings, 'DNC_FIELD_TYPES_MODULES', []):
    importlib.import_module(elem)
