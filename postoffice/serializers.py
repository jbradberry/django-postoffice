from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, validators

from . import models


class ContentTypeField(serializers.Field):
    def to_representation(self, value):
        return u'{value.app_label}.{value.model}'.format(value=value)

    def to_internal_value(self, data):
        app_label, model = data.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model)


class ReadOnlyDefault(object):
    def set_context(self, serializer_field):
        self.current_value = getattr(serializer_field.parent.instance,
                                     serializer_field.field_name, None)

    def __call__(self):
        return self.current_value

    def __repr__(self):
        return '%s()' % (self.__class__.__name__,)


# TODO: rename to InboxSerializer
class AddressSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True, default=ReadOnlyDefault())
    object_id = serializers.IntegerField(read_only=True,
                                         default=ReadOnlyDefault())

    unread_count = serializers.SerializerMethodField(required=False)
    inbox_count = serializers.SerializerMethodField(required=False)

    class Meta(object):
        model = models.Address
        fields = ('content_type', 'object_id', 'name', 'is_active',
                  'unread_count', 'inbox_count')
        read_only_fields = ('content_type', 'object_id', 'name', 'is_active',
                            'unread_count', 'inbox_count')

    def get_unread_count(self, obj):
        user = self._context['request'].user
        return models.MessageUser.objects.filter(
            address=obj, user=user, is_archived=False, is_read=False).count()

    def get_inbox_count(self, obj):
        user = self._context['request'].user
        return models.MessageUser.objects.filter(
            address=obj, user=user, is_archived=False).count()


# TODO: create an AddressSerializer for use with RecipientSerializer?

class RecipientSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.MessageAddress
        fields = ('address', 'address_type')


class MessageSerializer(serializers.ModelSerializer):
    header_addresses = RecipientSerializer(many=True)

    class Meta(object):
        model = models.Message
        fields = (
            'author_name', 'author_address', 'header_addresses', 'timestamp',
            'subject', 'parent', 'body', 'body_html'
        )
        read_only_fields = ('author_address', 'timestamp',
                            'parent', 'body_html')

    def create(self, validated_data):
        address_data = validated_data.pop('header_addresses', ())
        message = models.Message.objects.create(**validated_data)
        models.MessageAddress.objects.bulk_create([
            models.MessageAddress(message=message, **m_address)
            for m_address in address_data
        ])
        return message


class MessageUserSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)

    class Meta(object):
        model = models.MessageUser
        fields = ('message', 'user', 'is_read', 'is_archived')
        read_only_fields = ('message', 'user')
