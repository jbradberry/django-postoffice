from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (ObjectDoesNotExist, PermissionDenied,
                                    ImproperlyConfigured)
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from . import models, plugins, serializers

from rest_framework import generics, mixins


# /api/starsrace/3/messages/               (list and filter message, create new messages)
# /api/starsrace/3/messages/7/             (read a particular message)
# /api/starsrace/3/messages/7/read/        (mark message as read)
# /api/starsrace/3/messages/7/unread/      (mark message as unread)
# /api/starsrace/3/messages/7/archive/     (mark message as archived)
# /api/starsrace/3/messages/7/unarchive/   (mark message as unarchived)


# TODO: replace views with Django REST Framework

class AddressMixin(object):
    serializer_class = serializers.AddressSerializer
    queryset = models.Address.objects.all()

    def get_queryset(self):
        alias = self.kwargs.get('agent_alias')
        ct = plugins.agent_type(alias)

        return self.queryset.filter(content_type=ct, users=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()

        kwargs = {'object_id': self.kwargs.get('agent_pk')}
        obj = get_object_or_404(queryset, **kwargs)

        self.check_object_permissions(self.request, obj)
        return obj


class AddressListView(AddressMixin, generics.ListAPIView):
    # /api/starsrace/
    #permission_classes = (PluginPermissions,)
    pass


class AddressRetrieveView(AddressMixin, generics.RetrieveAPIView):
    # /api/starsrace/3/
    #permission_classes = (PluginPermissions,)
    pass
