from django.conf import settings

from django_netbox_confluence.updater.confluence_adapter import ConfluenceAdapter
from django_netbox_confluence.updater.exceptioins import WikiUpdateException
from django_netbox_confluence.models import NetBoxConfluenceField


class WikiPageUpdater(object):
    """
    Updates Wiki page when NetBox site page is updated.
    """

    def __init__(self, data):
        self.model_name = data['model']
        self.data = data
        self.page_title = self.generate_page_name(self.model_name)

        # Check whether settings for confluence updater exist.
        try:
            url = settings.DNC_CONFLUENCE_CREDENTIALS['url']
            username = settings.DNC_CONFLUENCE_CREDENTIALS['username']
            password = settings.DNC_CONFLUENCE_CREDENTIALS['password']
            space_key = settings.DNC_SPACE_KEY
        except (AttributeError, KeyError) as e:
            raise WikiUpdateException("{}: Please check configuration in settings file.".format(e))

        self.confluence = ConfluenceAdapter(url, username, password, space_key)

    @staticmethod
    def generate_page_name(model_name):
        """
        Generate page name on the Wiki.

        :type model_name: str
        :param model_name: Model name which was changed.

        :rtype: str
        :returns: Name of the page that should correspond to the changed model on the NetBox.
        """
        return "partials-{}".format(model_name)

    def get_field_chain(self):
        """
        Create fields chain. List of AbstractLinkedField derivatives.

        :raises: WikiUpdateException

        :rtype: list
        :returns: List of LinkedFields.
        """
        field_chain = list()
        # Get all fields that are configured by Django admin panel.
        fields = NetBoxConfluenceField.objects.filter(model_name=self.model_name)

        for field in fields:
            # Get field value form webhook request payload.
            try:
                if field.is_custom_field:
                    new_value = self.data['data']['custom_fields'][field.field_name]
                else:
                    new_value = self.data['data'][field.field_name]
            except KeyError:
                raise WikiUpdateException("Field {} is configured in updater but does not present in webhook payload."
                                          " May be `Is Custom Field` checkbox wrong state.".format(field))
            # Create AbstractLinkedField derivative class object.
            field_object = field.field_type_class(field.field_name, new_value, is_custom=field.is_custom_field)
            # Append to chain list.
            field_chain.append(field_object)

        return field_chain

    def update(self):
        """
        Update the data on the Wiki page to correspond the date from webhook.

        :raises: WikiUpdateException

        :rtype: void
        :returns: void
        """
        # Implemented as chain of responsibilities.
        # Each field will change its own field for which it is responsible and pass data to another one.
        # [LinkedField1, LinkedField2, ...]
        # (Wikis old content) -> LinkedField1 -> LinkedField2 -> ... -> (Wikis new content).
        field_chain = self.get_field_chain()

        page_id, page_content = self.confluence.get_page_or_create(self.page_title)

        # Provide page content to each field so each will update the content with it specific way.
        for field in field_chain:
            page_content = self.confluence.update_content_for_field(page_content, field)

        # After all fields are done with the changes update page content.
        self.confluence.update_page_content(page_id, self.page_title, page_content)
