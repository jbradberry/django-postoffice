from django.db import models
from django.contrib.contenttypes import generic


class Account(models.Model):
    name = models.CharField(max_length=100)
    closed = models.BooleanField(default=False)

    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    context = generic.GenericForeignKey()

    users = models.ManyToManyField("auth.User", through='AccountView')
    messages = models.ManyToManyField("Message", through='AccountMessage')

    def __unicode__(self):
        return self.name


class AccountView(models.Model):
    account = models.ForeignKey(Account)
    user = models.ForeignKey("auth.User")

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey("auth.User")
    from_name = models.CharField(max_length=100)

    sender = models.ForeignKey(Account, related_name='sent_messages')
    to = models.ManyToManyField(Account, related_name='to_received')
    bcc = models.ManyToManyField(Account, related_name='bcc_received')

    timestamp = models.DateTimeField()
    subject = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True)

    body = models.TextField()
    body_html = models.TextField()


class AccountMessage(models.Model):
    account = models.ForeignKey(Account)
    message = models.ForeignKey(Message)

    folder = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
