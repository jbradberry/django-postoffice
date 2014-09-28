from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^', include('postoffice.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
