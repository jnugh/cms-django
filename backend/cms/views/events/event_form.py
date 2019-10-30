"""
Form for creating or saving event objects and their corresponding event translation objects
"""

from datetime import time

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from ..utils.slug_utils import generate_unique_slug
from ...models import Event, EventTranslation, RecurrenceRule


class RecurrenceRuleForm(forms.ModelForm):
    has_recurrence_end_date = forms.BooleanField(required=False)

    class Meta:
        model = RecurrenceRule
        fields = [
            'frequency',
            'interval',
            'weekdays_for_weekly',
            'weekday_for_monthly',
            'week_for_monthly',
            'recurrence_end_date',
        ]
        widgets = {
            'recurrence_end_date': forms.DateInput(format='%d.%m.%Y'),
            'weekdays_for_weekly': forms.CheckboxSelectMultiple(
                choices=RecurrenceRule.WEEKDAYS
            ),
            'weekday_for_monthly': forms.Select(
                choices=RecurrenceRule.WEEKDAYS
            ),
            'week_for_monthly': forms.Select(
                choices=[(1, '1.'), (2, '2.'), (3, '3.'), (4, '4.'), (5, '5.')]
            )
        }

    # pylint: disable=arguments-differ
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            # Initialize BooleanField based on RecurrenceRule properties
            initial = kwargs.get('initial', {})
            kwargs['initial'] = {**initial,
                                 'has_recurrence_end_date': instance.has_recurrence_end_date,
                                 # Tuple conversion is necessary for CheckboxSelectMultiple widget
                                 'weekdays_for_weekly': tuple(instance.weekdays_for_weekly)
                                 }
        # Instantiate ModelForm
        super(RecurrenceRuleForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(RecurrenceRuleForm, self).clean()

        if not cleaned_data['has_recurrence_end_date']:
            cleaned_data['recurrence_end_date'] = None
        elif cleaned_data['recurrence_end_date'] is None:
            raise ValidationError(_('No recurrence end date selected'))

        return cleaned_data


class EventForm(forms.ModelForm):
    """
    Form class that can be rendered to create HTML code
    Inherits from django.forms.ModelForm, corresponds to the Event model
    """
    is_all_day = forms.BooleanField(required=False)
    is_recurring = forms.BooleanField(required=False)

    class Meta:
        model = Event
        fields = [
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'picture'
        ]
        widgets = {
            'start_date': forms.DateInput(format='%d.%m.%Y'),
            'end_date': forms.DateInput(format='%d.%m.%Y'),
            'start_time': forms.TimeInput(format='%H:%M'),
            'end_time': forms.TimeInput(format='%H:%M'),
        }

    # pylint: disable=arguments-differ
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            # Initialize BooleanFields based on Event properties
            initial = kwargs.get('initial', {})
            kwargs['initial'] = {**initial,
                                 'is_all_day': instance.is_all_day,
                                 'is_recurring': instance.is_recurring
                                 }
        # Instantiate ModelForm
        super(EventForm, self).__init__(*args, **kwargs)

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):

        region = kwargs.pop('region', None)
        recurrence_rule = kwargs.pop('recurrence_rule', None)

        if self.instance.id is None:
            # disable instant commit on saving because missing information would cause errors
            kwargs['commit'] = False

        event = super(EventForm, self).save(*args, **kwargs)

        if self.instance.id is None:
            # set initial values on event creation
            event.region = region

        event.recurrence_rule = recurrence_rule
        event.save()
        return event

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if cleaned_data['is_all_day'] or not cleaned_data['start_time']:
            cleaned_data['start_time'] = time.min

        if cleaned_data['is_all_day'] or not cleaned_data['end_time']:
            cleaned_data['end_time'] = time.max

        return cleaned_data


class EventTranslationForm(forms.ModelForm):
    """
    Form class that can be rendered to create HTML code
    Inherits from django.forms.ModelForm, corresponds to the EventTranslation model
    """

    PUBLIC_CHOICES = (
        (True, _('Public')),
        (False, _('Private'))
    )

    class Meta:
        model = EventTranslation
        fields = [
            'title',
            'slug',
            'description',
            'status',
            'public'
        ]

    def __init__(self, *args, **kwargs):

        # pop kwarg to make sure the super class does not get this param
        self.region = kwargs.pop('region', None)
        self.language = kwargs.pop('language', None)

        # to set the public value through the submit button, we have to overwrite the field value
        # for public. We could also do this in the save() function, but this would mean that it is
        # not recognized in changed_data. Check if POST data was submitted and the publish button
        # was pressed
        if len(args) == 1 and 'submit_publish' in args[0]:
            # copy QueryDict because it is immutable
            post = args[0].copy()
            # remove the old public value (might be False and update() does only append, not
            # overwrite)
            post.pop('public')
            # update the POST field with True (has to be a string to make sure the field is
            # recognized as changed)
            post.update({'public': 'True'})
            # set the args to POST again
            args = (post,)

        # instantiate ModelForm
        super(EventTranslationForm, self).__init__(*args, **kwargs)

        self.fields['public'].widget = forms.Select(choices=self.PUBLIC_CHOICES)

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):

        # pop kwargs to prevent error when calling super class
        event = kwargs.pop('event', None)
        user = kwargs.pop('user', None)

        if self.instance.id is None:
            # disable instant commit on saving because missing information would cause error
            kwargs['commit'] = False

        event_translation = super(EventTranslationForm, self).save(*args, **kwargs)

        if self.instance.id is None:
            # set initial values for new events
            event_translation.event = event
            event_translation.creator = user
            event_translation.language = self.language

        # finally save event_translation to database
        event_translation.save()
        return event_translation

    def clean_slug(self):
        return generate_unique_slug(self, 'event')
