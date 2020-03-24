from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^', include('postoffice.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)
