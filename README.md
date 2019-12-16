`NetBox -> Confluence Wiki` Connector
=====================================

`Alrescha` is a synchronization tool which helps synchronize data described on the NetBox and appropriate pages on
Confluence Wiki.
When some page is edited on the NetBox the webhook is fired and calls the `Alreshca` endpoint which gathers the data
 and updates specific page for updated model on the Wiki. For each field/input it creates MultiExcerpt macro
  which then can be used in other pages providing "dynamic" content.

`Alrescha` uses NetBox webhooks in order to get information about changes and update the data on the Wiki.
For that purpose it is needed to create webhook on the NetBox admin.

`Alrescha` runs as a web application atop the [Django](https://www.djangoproject.com/)
For a complete list of requirements, see `requirements.txt`. The code is available [on GitHub](https://github.com/hovodab/alrescha).


# Installation

```bash
$ pip install -r requirements.txt
```
