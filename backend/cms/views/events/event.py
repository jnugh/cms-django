from datetime import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from .event_form import EventForm, EventTranslationForm, RecurrenceRuleForm
from ...decorators import region_permission_required
from ...models import Region, Language, Event, EventTranslation, RecurrenceRule


@method_decorator(login_required, name='dispatch')
@method_decorator(region_permission_required, name='dispatch')
class EventView(PermissionRequiredMixin, TemplateView):
    permission_required = 'cms.view_events'
    raise_exception = True

    template_name = 'events/event.html'
    base_context = {'current_menu_item': 'events'}

    def get(self, request, *args, **kwargs):
        region = Region.objects.get(slug=kwargs.get('region_slug'))
        language = Language.objects.get(code=kwargs.get('language_code'))

        # get event and event translation objects if they exist, otherwise objects are None
        event_instance = Event.objects.filter(id=kwargs.get('event_id')).first()
        recurrence_rule_instance = RecurrenceRule.objects.filter(event=event_instance).first()
        event_translation_instance = EventTranslation.objects.filter(
            event=event_instance,
            language=language
        ).first()

        recurrence_rule_form = RecurrenceRuleForm(
            instance=recurrence_rule_instance
        )
        event_form = EventForm(
            instance=event_instance
        )
        event_translation_form = EventTranslationForm(
            instance=event_translation_instance
        )

        return render(request, self.template_name, {
            'event_form': event_form,
            'event_translation_form': event_translation_form,
            'recurrence_rule_form': recurrence_rule_form,
            'event': event_instance,
            'language': language,
            'languages': region.languages,
            **self.base_context
        })

    # pylint: disable=too-many-locals,too-many-branches
    def post(self, request, *args, **kwargs):
        region = Region.objects.get(slug=kwargs.get('region_slug'))
        language = Language.objects.get(code=kwargs.get('language_code'))

        event_instance = Event.objects.filter(id=kwargs.get('event_id')).first()
        recurrence_rule_instance = RecurrenceRule.objects.filter(event=event_instance).first()
        event_translation_instance = EventTranslation.objects.filter(
            event=event_instance,
            language=language
        ).first()

        recurrence_rule_form = RecurrenceRuleForm(
            request.POST,
            instance=recurrence_rule_instance
        )
        event_form = EventForm(
            request.POST,
            instance=event_instance,
        )
        event_translation_form = EventTranslationForm(
            request.POST,
            instance=event_translation_instance,
            region=region,
            language=language
        )
        # TODO: error handling
        if (
            event_form.is_valid() and
            event_translation_form.is_valid() and
            (
                recurrence_rule_form.is_valid() or
                not event_form.cleaned_data['is_recurring']
            )
        ):

            if event_form.cleaned_data['is_recurring']:
                recurrence_rule = recurrence_rule_form.save()
            else:
                recurrence_rule = None

            event = event_form.save(
                region=region,
                recurrence_rule=recurrence_rule
            )
            event_translation = event_translation_form.save(
                event=event,
                user=request.user
            )

            if event_form.has_changed() or event_translation_form.has_changed():
                published = event_translation.public \
                            and 'public' in event_translation_form.changed_data
                if not event_instance:
                    if published:
                        messages.success(request,
                                         _('Event was successfully created and published.'))
                    else:
                        messages.success(request, _('Event was successfully created.'))
                elif not event_translation_instance:
                    if published:
                        messages.success(request,
                                         _('Event translation was successfully created and published.'))
                    else:
                        messages.success(request, _('Event translation was successfully created.'))
                else:
                    if published:
                        messages.success(request, _('Event translation was successfully published.'))
                    else:
                        messages.success(request, _('Event translation was successfully saved.'))
            else:
                messages.info(request, _('No changes detected.'))

            return redirect('edit_event', **{
                'event_id': event.id,
                'region_slug': region.slug,
                'language_code': language.code,
            })

        messages.error(request, _('Errors have occurred.'))

        return render(request, self.template_name, {
            **self.base_context,
            'event_form': event_form,
            'event_translation_form': event_translation_form,
            'recurrence_rule_form': recurrence_rule_form,
            'event': event_instance,
            'language': language,
            'languages': region.languages,
        })
