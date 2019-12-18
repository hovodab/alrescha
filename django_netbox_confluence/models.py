from django.db import models
from django_netbox_confluence.updater.linked_fields import ABCLinkedFieldMeta


class NetBoxConfluenceField(models.Model):
    """
    Represents fields that should be synchronized/updated when they are edited on NetBox.
    """
    TYPE_CHOICES = ((name, the_class.verbose_name)
                    for name, the_class in ABCLinkedFieldMeta.linked_field_classes.items())
    model_name = models.CharField(max_length=255, verbose_name='Model Name', help_text="Model Name")
    field_type = models.CharField(max_length=255, verbose_name='Type', choices=TYPE_CHOICES, help_text="Field Type")
    is_custom_field = models.BooleanField(verbose_name='Is Custom Field', help_text="Is the field `custom field`?",
                                          default=False)
    field_name = models.CharField(max_length=255, verbose_name='Field')

    class Meta:
        unique_together = ('model_name', 'field_name', 'is_custom_field')

    def __str__(self):
        return "{model} > {custom}{field} ({type})".format(model=self.model_name,
                                                           custom=("custom_" if self.is_custom_field else ""),
                                                           field=self.field_name,
                                                           type=self.field_type)

    @property
    def field_type_class(self):
        return ABCLinkedFieldMeta.linked_field_classes[self.field_type]
