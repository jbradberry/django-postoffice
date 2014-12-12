from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (ObjectDoesNotExist, PermissionDenied,
                                    ImproperlyConfigured)
from django.views.generic import ListView, DetailView, CreateView
from django.http import Http404
from django.conf import settings

from . import models


class ContextMixin(object):
    model = models.Message

    context_slug_field = 'slug'

    slug_context_kwarg = 'context_slug'
    pk_context_kwarg = 'context_pk'

    def get_context(self):
        context = None

        context_content_type = self.kwargs.get('context_content_type')
        if context_content_type is None:
            raise ImproperlyConfigured(
                "{0} is missing a valid context_content_type".format(
                    self.__class__.__name__))

        try:
            app_label, model = realm_content_type.split('.')
            model = model.lower()
            self.context_type = ContentType.objects.get(app_label=app_label,
                                                        model=model)
        except (ObjectDoesNotExist, ValueError) as e:
            raise ImproperlyConfigured(
                "{0} is missing a valid context_content_type".format(
                    self.__class__.__name__))

        context_pk = self.kwargs.get(self.pk_context_kwarg)
        context_slug = self.kwargs.get(self.slug_context_kwarg)

        if context_pk is not None:
            opts = {'pk': context_pk}
        elif context_slug is not None:
            opts = {self.context_slug_field: context_slug}
        else:
            opts = None

        if opts:
            try:
                context = self.context_type.get_object_for_this_type(**opts)
            except ObjectDoesNotExist:
                raise Http404(
                    "No {0} found matching this query.".format(
                        self.context_type.__class__.__name__))

        return context

    def get_address(self):
        address = None

        if self.context:
            try:
                address = models.Address.objects.get(
                    content_type=self.context_type, object_id=self.context.id)
            except ObjectDoesNotExist:
                raise Http404("No matching address found.")

            if not address.users.filter(user=self.request.user).exists():
                raise PermissionDenied(
                    "You are not authorized to view this account.")

        return address

    def get_queryset(self):
        queryset = super(ContextMixin, self).get_queryset()

        if self.address:
            return queryset.filter(addresses=self.address)
        return queryset

    def get_context_data(self, **kwargs):
        context = {'address': self.address,
                   'context': self.context,
                   'current_app': self.account.content_type.app_label}
        context.update(kwargs)
        return super(ContextMixin, self).get_context_data(**context)

    def get(self, request, *args, **kwargs):
        self.context = self.get_context()
        self.address = self.get_address()
        return super(ContextMixin, self).get(request, *args, **kwargs)


class MessageListView(ContextMixin, ListView):
    paginate_by = 25


class MessageDetailView(ContextMixin, DetailView):
    pass


class MessageCreateView(ContextMixin, CreateView):
    form_class = forms.MessageForm

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super(MessageCreateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.context = self.get_context()
        self.account = self.get_account()
        return super(MessageCreateView, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageCreateView, self).dispatch(*args, **kwargs)
