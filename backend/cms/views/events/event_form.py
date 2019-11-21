"""
Form for creating or saving event objects and their corresponding event translation objects
"""
import logging

from datetime import time

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from ..utils.slug_utils import generate_unique_slug
from ...constants import status, weekdays, weeks
from ...models import Event, EventTranslation, RecurrenceRule

logger = logging.getLogger(__name__)


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
            'weekdays_for_weekly': forms.CheckboxSelectMultiple(choices=weekdays.CHOICES),
            'weekday_for_monthly': forms.Select(choices=weekdays.CHOICES),
            'week_for_monthly': forms.Select(choices=weeks.CHOICES)
        }

    # pylint: disable=arguments-differ
    def __init__(self, *args, **kwargs):
        logger.info(
            'RecurrenceRuleForm instantiated with args %s, kwargs %s',
            args,
            kwargs
        )

        # Instantiate ModelForm
        super(RecurrenceRuleForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            # Initialize BooleanField based on RecurrenceRule properties
            self.fields['has_recurrence_end_date'].initial = bool(self.instance.recurrence_end_date)

    def clean(self):
        cleaned_data = super(RecurrenceRuleForm, self).clean()

        if not cleaned_data['has_recurrence_end_date']:
            cleaned_data['recurrence_end_date'] = None
        elif cleaned_data['recurrence_end_date'] is None:
            raise ValidationError(_('No recurrence end date selected'))

        return cleaned_data

    def has_changed(self):
        # Handle weekdays_for_weekly data separately from the other data because has_changed doesn't work
        # with CheckboxSelectMultiple widgets and ArrayFields out of the box
        try:
            # Have to remove the corresponding field name from self.changed_data
            self.changed_data.remove('weekdays_for_weekly')
        except ValueError:
            return super(RecurrenceRuleForm, self).has_changed()

        value = self.fields['weekdays_for_weekly'].widget.value_from_datadict(self.data, self.files, self.add_prefix('weekdays_for_weekly'))
        initial = self['weekdays_for_weekly'].initial
        value_list = list(value) if value is not None else None
        initial_list = list(initial) if initial is not None else None
        # Sort the lists because they could have the same content in a different order
        value_list.sort()
        initial_list.sort()
        if self.fields['weekdays_for_weekly'].has_changed(initial_list, value_list):
            self.changed_data.append('weekdays_for_weekly')
        return bool(self.changed_data)


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
        logger.info(
            'EventForm instantiated with args %s, kwargs %s',
            args,
            kwargs
        )

        # Instantiate ModelForm
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            # Initialize BooleanFields based on Event properties
            self.fields['is_all_day'].initial = (self.instance.start_time == time.min and self.instance.end_time == time.max)
            self.fields['is_recurring'].initial = bool(self.instance.recurrence_rule)

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        logger.info(
            'EventForm saved with args %s, kwargs %s, cleaned data %s and changed data %s',
            args,
            kwargs,
            self.cleaned_data,
            self.changed_data
        )

        region = kwargs.pop('region', None)
        recurrence_rule = kwargs.pop('recurrence_rule', None)

        if not self.instance.id:
            # disable instant commit on saving because missing information would cause errors
            kwargs['commit'] = False

        event = super(EventForm, self).save(*args, **kwargs)

        if not self.instance.id:
            # set initial values on event creation
            event.region = region

        if event.recurrence_rule and not recurrence_rule:
            # Delete old recurrence rule from database in order to not spam the database with unused objects
            event.recurrence_rule.delete()
        event.recurrence_rule = recurrence_rule
        event.save()
        return event

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if cleaned_data['is_all_day'] or 'start_time' not in cleaned_data:
            cleaned_data['start_time'] = time.min

        if cleaned_data['is_all_day'] or 'end_time' not in cleaned_data:
            cleaned_data['end_time'] = time.max

        return cleaned_data

    def has_changed(self):
        # If is_all_day is set, the initial value for end_time is 23:59 but the new value is 23:59:59
        # because of how the widget is set. This results in end_time always being in self.changed data.
        # Therefore ignore changes to end_time if the event initially was all day long and still is.
        if self.fields['is_all_day'].widget.value_from_datadict(self.data, self.files, self.add_prefix('is_all_day')) \
            and self['is_all_day'].initial:
            try:
                self.changed_data.remove('end_time')
            except ValueError:
                pass
        return super(EventForm, self).has_changed()


class EventTranslationForm(forms.ModelForm):
    """
    Form class that can be rendered to create HTML code
    Inherits from django.forms.ModelForm, corresponds to the EventTranslation model
    """

    class Meta:
        model = EventTranslation
        fields = [
            'title',
            'slug',
            'description',
            'status',
            'minor_edit',
        ]

    def __init__(self, *args, **kwargs):
        logger.info(
            'EventTranslationForm instantiated with args %s, kwargs %s',
            args,
            kwargs
        )

        # pop kwarg to make sure the super class does not get this param
        self.region = kwargs.pop('region', None)
        self.language = kwargs.pop('language', None)
        disabled = kwargs.pop('disabled', None)

        # To set the status value through the submit button, we have to overwrite the field value for status.
        # We could also do this in the save() function, but this would mean that it is not recognized in changed_data.
        # Check if POST data was submitted
        if len(args) == 1:
            # Copy QueryDict because it is immutable
            post = args[0].copy()
            # Update the POST field with the status corresponding to the submitted button
            if 'submit_draft' in args[0]:
                post.update({'status': status.DRAFT})
            elif 'submit_review' in args[0]:
                post.update({'status': status.REVIEW})
            elif 'submit_public' in args[0]:
                post.update({'status': status.PUBLIC})
            # Set the args to POST again
            args = (post,)

        # instantiate ModelForm
        super(EventTranslationForm, self).__init__(*args, **kwargs)

        # If form is disabled because the user has no permissions to edit the page, disable all form fields
        if disabled:
            for _, field in self.fields.items():
                field.disabled = True

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        logger.info(
            'EventTranslationForm saved with args %s, kwargs %s, cleaned data %s and changed data %s',
            args,
            kwargs,
            self.cleaned_data,
            self.changed_data
        )

        # pop kwargs to prevent error when calling super class
        event = kwargs.pop('event', None)
        user = kwargs.pop('user', None)

        if not self.instance.id:
            # disable instant commit on saving because missing information would cause error
            kwargs['commit'] = False

        event_translation = super(EventTranslationForm, self).save(*args, **kwargs)

        if not self.instance.id:
            # set initial values for new events
            event_translation.event = event
            event_translation.creator = user
            event_translation.language = self.language

        # Only create new version if content changed
        if not {'slug', 'title', 'description'}.isdisjoint(self.changed_data):
            event_translation.version = event_translation.version + 1
            event_translation.pk = None
        # finally save event_translation to database
        event_translation.save()
        return event_translation

    def clean_slug(self):
        return generate_unique_slug(self, 'event')
