from django.urls import path

from . import views


app_name = 'django_netbox_confluence'
urlpatterns = [
    path('model_change_trigger/', views.ModelChangeTriggerView.as_view()),
]
