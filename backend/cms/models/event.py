"""Class defining event-related database models

Raises:
    ValidationError: Raised when an value does not match the requirements
"""
from datetime import datetime, time, date

from dateutil.rrule import weekday, rrule
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .language import Language
from .poi import POI
from .region import Region


class RecurrenceRule(models.Model):
    """
    Object to define the recurrence frequency
    Args:
        models ([type]): [description]
    Raises:
        ValidationError: Error raised when weekdays_for_weekly does not fit into the range
        from 0 to 6 or when the value of weekdays_for_monthly isn't between -5 and 5.
    """

    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    JANUARY = 0
    FEBRUARY = 1
    MARCH = 2
    APRIL = 3
    MAY = 4
    JUNE = 5
    JULY = 6
    AUGUST = 7
    SEPTEMBER = 8
    OCTOBER = 9
    NOVEMBER = 10
    DECEMBER = 11

    FREQUENCY = (
        (DAILY, 'Täglich'),
        (WEEKLY, 'Wöchentlich'),
        (MONTHLY, 'Monatlich'),
        (YEARLY, 'Jährlich')
    )

    WEEKDAYS = (
        (MONDAY, 'Montag'),
        (TUESDAY, 'Dienstag'),
        (WEDNESDAY, 'Mittwoch'),
        (THURSDAY, 'Donnerstag'),
        (FRIDAY, 'Freitag'),
        (SATURDAY, 'Samstag'),
        (SUNDAY, 'Sonntag')
    )

    MONTHS = (
        (JANUARY, 'Januar'),
        (FEBRUARY, 'Februar'),
        (MARCH, 'März'),
        (APRIL, 'April'),
        (MAY, 'Mai'),
        (JUNE, 'Juni'),
        (JULY, 'Juli'),
        (AUGUST, 'August'),
        (SEPTEMBER, 'September'),
        (OCTOBER, 'Oktober'),
        (NOVEMBER, 'November'),
        (DECEMBER, 'Dezember')
    )

    frequency = models.CharField(max_length=7, choices=FREQUENCY, blank=True)
    interval = models.IntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    weekdays_for_weekly = ArrayField(
        models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)]),
        null=True, blank=True
    )
    weekday_for_monthly = models.IntegerField(null=True, blank=True)
    week_for_monthly = models.IntegerField(
        null=True,
        validators=[MinValueValidator(-5), MaxValueValidator(5)],
        blank = True
    )
    recurrence_end_date = models.DateField(null=True, default=None, blank=True)

    @property
    def has_recurrence_end_date(self):
        return self.recurrence_end_date is not None

    def clean(self):
        if self.frequency == RecurrenceRule.WEEKLY \
                and (self.weekdays_for_weekly is None or len(self.weekdays_for_weekly) == 0):
            raise ValidationError(_('No weekdays selected for weekly recurrence'))
        if self.frequency == 'monthly' and (
                self.weekday_for_monthly is None or self.week_for_monthly is None):
            raise ValidationError(_('No weekday or no week selected for monthly recurrence'))


class Event(models.Model):
    """Database object representing an event with name, date and the option to add recurrency.

    Args:
        models : Database model inherit from the standard django models

    Raises:
        ValidationError: Raised if the recurrence end date is after the start date
        ValidationError: Raised if start or end date isn't null when the other one is
        ValidationError: Raised if the end date is before the start date
    """

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    location = models.ForeignKey(POI, on_delete=models.PROTECT, null=True, blank=True)
    start_date = models.DateField()
    start_time = models.TimeField(blank=True)
    end_date = models.DateField()
    end_time = models.TimeField(blank=True)
    recurrence_rule = models.OneToOneField(RecurrenceRule, null=True, on_delete=models.SET_NULL)
    picture = models.ImageField(null=True, blank=True, upload_to='events/%Y/%m/%d')

    def clean(self):
        if self.start_date is None or self.end_date is None:
            raise ValidationError(_('Start date and end date mustn\'t be empty'), code='required')
        if self.recurrence_rule is not None and self.recurrence_rule.recurrence_end_date is not None:
            if self.recurrence_rule.recurrence_end_date <= self.start_date:
                raise ValidationError(_('Recurrence end date has to be after the event\'s start date'), code='invalid')
        if (self.start_time is None) ^ (self.end_time is None):
            raise ValidationError(_('Start time and end time must either be both empty or both filled out'), code='invalid')
        if self.end_date < self.start_date or (
                self.end_date == self.start_date and self.end_time < self.start_time):
            raise ValidationError(_('The end of the event can\'t be before the start of the event'), code='invalid')

    @property
    def languages(self):
        event_translations = self.event_translations.prefetch_related('language').all()
        languages = []
        for event_translation in event_translations:
            languages.append(event_translation.language)
        return languages

    @property
    def is_recurring(self):
        return self.recurrence_rule is not None

    @property
    def is_all_day(self):
        return self.start_time == time.min and self.end_time == time.max

    def get_translation(self, language_code):
        """Provides a translation of the Event
        Returns:
            event_translation: Translation of this event
        """
        try:
            event_translation = self.event_translations.get(language__code=language_code)
        except ObjectDoesNotExist:
            event_translation = None
        return event_translation

    @classmethod
    def get_list(cls, region_slug):
        """
        Function: Get List View

        Args:
            region_slug: slug of the region the event belongs to

        Returns:
            [events]: Array of all Events
        """
        events = cls.objects.all().prefetch_related(
            'event_translations'
        ).filter(
            region__slug=region_slug
        )
        return events

    def get_occurrences(self, start, end):
        """
        Returns start datetimes of occurrences of the event that overlap with [start, end]
        Expects start < end
        :type start: datetime
        :type end: datetime
        :return:
        """
        event_start = datetime.combine(self.start_date,
                                       self.start_time if self.start_time else time.min)
        event_end = datetime.combine(self.end_date, self.end_time if self.end_time else time.max)
        event_span = event_end - event_start
        recurrence = self.recurrence_rule
        if recurrence is not None:
            until = min(end, datetime.combine(recurrence.recurrence_end_date
                                              if recurrence.recurrence_end_date
                                              else date.max, time.max))
            if recurrence.frequency in (RecurrenceRule.DAILY, RecurrenceRule.YEARLY):
                occurrences = rrule(recurrence.frequency,
                                    dtstart=event_start,
                                    interval=recurrence.interval,
                                    until=until)
            elif recurrence.frequency == RecurrenceRule.WEEKLY:
                occurrences = rrule(recurrence.frequency,
                                    dtstart=event_start,
                                    interval=recurrence.interval,
                                    byweekday=recurrence.weekdays_for_weekly,
                                    until=until)
            else:
                occurrences = rrule(recurrence.frequency,
                                    dtstart=event_start,
                                    interval=recurrence.interval,
                                    byweekday=weekday(recurrence.weekday_for_monthly,
                                                      recurrence.week_for_monthly),
                                    until=until)
            return [x for x in occurrences if start <= x <= end or start <= x + event_span <= end]
        return [event_start] if start <= event_start <= end or start <= event_end <= end else []

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_events', 'Can view events'),
            ('edit_events', 'Can edit events'),
            ('publish_events', 'Can publish events')
        )


class EventTranslation(models.Model):
    """
    Database object representing an event tranlsation
    """
    event = models.ForeignKey(Event, related_name='event_translations', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    STATUS = (
        ('draft', _('Draft')),
        ('in-review', _('Pending Review')),
        ('reviewed', _('Finished Review')),
    )
    status = models.CharField(max_length=9, choices=STATUS, default='draft')
    title = models.CharField(max_length=250)
    description = models.TextField()
    language = models.ForeignKey(
        Language,
        related_name='event_translations',
        on_delete=models.CASCADE
    )
    currently_in_translation = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=0)
    minor_edit = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def permalink(self):
        return self.event.region.slug + '/' \
               + self.language.code + '/' \
               + self.slug + '/'

    def __str__(self):
        return self.title

    class Meta:
        default_permissions = ()
