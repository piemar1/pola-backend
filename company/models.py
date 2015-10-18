# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Count
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import PassThroughManager
import reversion


class IntegerRangeField(models.IntegerField):

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        super(models.IntegerField, self).__init__(*args, **kwargs)
        self.min_value, self.max_value = min_value, max_value

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value,
                    'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class CompanyQuerySet(models.query.QuerySet):

    def get_or_create(self, commit_desc=None, commit_user=None, *args, **kwargs):
        if not commit_desc:
            return super(CompanyQuerySet, self).get_or_create(*args, **kwargs)

        with transaction.atomic(), reversion.create_revision(manage_manually=True):
            obj = super(CompanyQuerySet, self).get_or_create(*args, **kwargs)
            reversion.default_revision_manager.save_revision([obj[0]],
                comment=commit_desc, user=commit_user)
            return obj

    def with_query_count(self):
        return self.annotate(query_count=Count('product__query__id'))


class Company(models.Model):
    nip = models.CharField(max_length=10, db_index=True, null=True,
                           blank=True, verbose_name=_(u"NIP/Tax ID"))
    name = models.CharField(max_length=128, null=True, blank=True,
                            db_index=True,
                            verbose_name=
                            _(u"Nazwa (pobrana z ILiM)"))
    official_name = models.CharField(max_length=128, blank=True, null=True,
                                     verbose_name=_(u"Nazwa rejestrowa"))
    common_name = models.CharField(max_length=128, blank=True,
                                   verbose_name=_(u"Nazwa dla użytkownika"))
    address = models.TextField(null=True, blank=True)

    plCapital = IntegerRangeField(
        verbose_name=_(u"Udział polskiego kapitału"),
        min_value=0, max_value=100, null=True, blank=True)
    plCapital_notes = models.TextField(
        _(u"Więcej nt. udziału polskiego kapitału"), null=True, blank=True)

    plWorkers = IntegerRangeField(
        verbose_name=_(u"Miejsce produkcji"), min_value=0,
        max_value=100, null=True, blank=True,
        choices=((0,_(u"0 - Nie produkuje w Polsce")),
                 (100,_(u"100 - Produkuje w Polsce"))))
    plWorkers_notes = models.TextField(
        _(u"Więcej nt. miejsca produkcji"), null=True, blank=True)

    plRnD = IntegerRangeField(
        verbose_name=_(u"Wysokopłatne miejsca pracy"), min_value=0,
        max_value=100, null=True, blank=True,
        choices=((0,_(u"0 - Nie tworzy wysokopłatnych miejsc pracy w Polsce")),
                 (100,_(u"100 - Tworzy wysokopłatne miejsca pracy w Polsce"))))
    plRnD_notes = models.TextField(
        _(u"Więcej nt. wysokopłatnych miejsc pracy"), null=True, blank=True)

    plRegistered = IntegerRangeField(
        verbose_name=_(u"Miejsce rejestracji"), min_value=0, max_value=100,
        null=True, blank=True,
        choices=((0,_(u"0 - Firma zarejestrowana za granicą")),
                 (100,_(u"100 - Firma zarejestrowana w Polsce"))))
    plRegistered_notes = models.TextField(
        _(u"Więcej nt. miejsca rejestracji"), null=True, blank=True)

    plNotGlobEnt = IntegerRangeField(
        verbose_name=_(u"Struktura kapitałowa"), min_value=0,
        max_value=100, null=True, blank=True,
        choices=((0,_(u"0 - Firma jest częścią zagranicznego koncernu")),
                 (100,_(u"100 - Firma nie jest częścią zagranicznego koncernu"))))
    plNotGlobEnt_notes = models.TextField(
        _(u"Więcej nt. struktury kapitałowej"), null=True, blank=True)
    verified = models.BooleanField(default=False)

    objects = PassThroughManager.for_queryset_class(CompanyQuerySet)()

    def to_dict(self):
        dict = model_to_dict(self)
        return dict

    def get_absolute_url(self):
        return reverse('company:detail', args=[self.pk])

    def __unicode__(self):
        return self.common_name or self.official_name or self.name

    def save(self, commit_desc=None, commit_user=None, *args, **kwargs):
        if not commit_desc:
            return super(Company, self).save(*args, **kwargs)

        with transaction.atomic(), reversion.create_revision(manage_manually=True):
            obj = super(Company, self).save(*args, **kwargs)
            reversion.default_revision_manager.save_revision([self],
                comment=commit_desc, user=commit_user )
            return obj

    class Meta:
        verbose_name = _(u"Producent")
        verbose_name_plural = _(u"Producenci")

reversion.register(Company)
