# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-17 15:02:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-19 16:40:49
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language
from django.db.models import Case, When, Exists, F, OuterRef, Subquery
from django.db import models

from .decorators import tof_filter, tof_prefetch


class DecoratedMixIn:
    @tof_filter  # noqa
    def filter(self, *args, **kwargs):  # noqa
        return super().filter(*args, **kwargs)

    @tof_filter  # noqa
    def exclude(self, *args, **kwargs):
        return super().exclude(*args, **kwargs)

    @tof_filter  # noqa
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @tof_filter  # noqa
    def order_by(self, *args):
        from .models import Translation

        content_type = ContentType.objects.get_for_model(self.model)

        new_args = []
        for arg in args:
            field_name, order = arg, ''
            if arg.startswith('-') or arg.startswith('+'):
                field_name, order = arg[1:], arg[0]

            if field_name == '?':
                new_args.append('?')
                continue

            new_args.append(f'{order}_{field_name}')

            translation = Translation.objects.filter(content_type=content_type, lang=get_language(),
                                                     field__name=field_name)

            self = self.annotate(**{f'_{field_name}': Case(
                When(
                    Exists(translation.filter(object_id=OuterRef('pk'))),
                    then=Subquery(translation.filter(object_id=OuterRef('pk')).values('value'))
                ),
                default=F(field_name),
                output_field=models.CharField(),
            )})

        return super().order_by(*new_args)


class TranslationsQuerySet(DecoratedMixIn, models.QuerySet):
    pass


class TranslationManager(DecoratedMixIn, models.Manager):
    default_name = 'trans_objects'
    _queryset_class = TranslationsQuerySet

    def __init__(self, name=None):
        self.default_name = name or self.default_name
        super().__init__()

    @tof_prefetch()
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)
