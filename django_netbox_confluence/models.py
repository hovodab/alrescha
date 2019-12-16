from django.db import models
from django_netbox_confluence.updater.linked_fields import ABCLinkedFieldMeta


class NetboxConfluenceField(models.Model):
    TYPE_CHOICES = ((name, the_class.verbose_name)
                    for name, the_class in ABCLinkedFieldMeta.linked_field_classes.items())

    model_name = models.CharField(max_length=255, help_text="Model Name")
    field_type = models.CharField(max_length=255, choices=TYPE_CHOICES, help_text="Field Type")
    field_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('model_name', 'field_name',)
