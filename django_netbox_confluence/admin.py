from django.contrib import admin

from django_netbox_confluence.models import NetBoxConfluenceField


class NetBoxConfluenceFieldAdmin(admin.ModelAdmin):
    pass


admin.site.register(NetBoxConfluenceField, NetBoxConfluenceFieldAdmin)
