from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (ObjectDoesNotExist, PermissionDenied,
                                    ImproperlyConfigured)
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from . import models, plugins, serializers

from rest_framework import generics, mixins, status
from rest_framework.response import Response


# TODO: create an endpoint that provides a list of valid target
# addresses for a particular agent to mail to (/api/starsrace/42/addresses/)

# TODO: add a method to the plugin that provides the list of target
# agents for a given agent

# TODO: create an endpoint for a realm administrator to create addresses?


# /api/starsrace/42/messages/7/             (read a particular message)
# /api/starsrace/42/messages/7/read/        (mark message as read)
# /api/starsrace/42/messages/7/unread/      (mark message as unread)
# /api/starsrace/42/messages/7/archive/     (mark message as archived)
# /api/starsrace/42/messages/7/unarchive/   (mark message as unarchived)


# TODO: replace views with Django REST Framework

class AddressQuerysetMixin(object):
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


class AddressListView(AddressQuerysetMixin, generics.ListAPIView):
    # /api/starsrace/
    #permission_classes = (PluginPermissions,)
    pass


class AddressRetrieveView(AddressQuerysetMixin, generics.RetrieveAPIView):
    # /api/starsrace/42/
    #permission_classes = (PluginPermissions,)
    pass


class AddressMixin(object):
    def get_address(self):
        alias = self.kwargs.get('agent_alias')
        ct = plugins.agent_type(alias)
        pk = self.kwargs.get('agent_pk')

        address = get_object_or_404(
            models.Address, content_type=ct, object_id=pk)

        if not address.users.filter(id=self.request.user.pk).exists():
            raise PermissionDenied

        return address


class MessageCreateView(AddressMixin, generics.CreateAPIView):
    # /api/starsrace/42/post/
    serializer_class = serializers.MessageSerializer
    queryset = models.Message.objects.all()

    def create(self, request, *args, **kwargs):
        address = self.get_address()

        instance = models.Message(author=self.request.user,
                                  author_address=address)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageListView(AddressMixin, generics.ListAPIView):
    # /api/starsrace/42/messages/
    serializer_class = serializers.MessageUserSerializer
    queryset = models.MessageUser.objects.all()

    def get_queryset(self):
        address = self.get_address()

        return self.queryset.filter(
            user=self.request.user,
            message__addresses=address
        )
