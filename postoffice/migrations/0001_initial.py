# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
                ('users', models.ManyToManyField(related_name='postoffice_addresses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('subject', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('body_html', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MessageAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_type', models.CharField(default=b'to', max_length=3, choices=[(b'to', b'To'), (b'cc', b'Cc'), (b'bcc', b'Bcc')])),
                ('address', models.ForeignKey(to='postoffice.Address')),
                ('message', models.ForeignKey(related_name='header_addresses', to='postoffice.Message')),
            ],
        ),
        migrations.CreateModel(
            name='MessageUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_read', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='postoffice.Message')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='addresses',
            field=models.ManyToManyField(to='postoffice.Address', through='postoffice.MessageAddress'),
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='author_address',
            field=models.ForeignKey(related_name='sentmail', to='postoffice.Address', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='parent',
            field=models.ForeignKey(to='postoffice.Message', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='recipients',
            field=models.ManyToManyField(related_name='postoffice_messages', through='postoffice.MessageUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
