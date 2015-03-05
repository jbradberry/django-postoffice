from django.db import models
from django.contrib.contenttypes import generic


class Address(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType", null=True)
    object_id = models.PositiveIntegerField(null=True)
    context = generic.GenericForeignKey()

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Address has a m2m with User so that the API can easily get from
    # a user to the allowed messages.
    users = models.ManyToManyField("auth.User",
                                   related_name='postoffice_addresses')

    def __unicode__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey("auth.User")
    author_name = models.CharField(max_length=100)

    addresses = models.ManyToManyField(Address, through='MessageAddress')

    timestamp = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True)

    body = models.TextField()
    body_html = models.TextField()

    recipients = models.ManyToManyField("auth.User", through='MessageUser',
                                        related_name='postoffice_messages')


class MessageAddress(models.Model):
    TO = 'to'
    CC = 'cc'
    BCC = 'bcc'
    ADDRESS_CHOICES = ((TO, 'To'),
                       (CC, 'Cc'),
                       (BCC, 'Bcc'),)

    message = models.ForeignKey(Message)
    address = models.ForeignKey(Address)
    address_type = models.CharField(max_length=3, choices=ADDRESS_CHOICES,
                                    default=TO)


class MessageUser(models.Model):
    # Manages a user's particular states of the messages they have
    # received, seperately from all of the other users that may have
    # access to an agent's messages.

    message = models.ForeignKey(Message)
    user = models.ForeignKey("auth.User")

    address = models.ForeignKey(Address)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
