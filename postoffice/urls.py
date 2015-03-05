from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<agent_alias>[-\w]+)/$', views.AddressListView.as_view(),
        name='address_list'),
    url(r'^(?P<agent_alias>[-\w]+)/(?P<agent_pk>\d+)/$',
        views.AddressRetrieveView.as_view(),
        name='address_detail'),
)
