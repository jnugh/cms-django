from django import template

register = template.Library()


@register.filter
def event_translation_title(event, language):
    all_event_translations = event.event_translations
    event_translation = all_event_translations.filter(language__code=language.code)
    if event_translation.exists():
        return event_translation.first().title
    if all_event_translations.exists():
        event_translation = all_event_translations.first()
        return '{title} ({language})'.format(
            title=event_translation.title,
            language=event_translation.language
        )
    return ''


@register.filter
def event_translation_creator(event, language):
    all_event_translations = event.event_translations
    event_translation = all_event_translations.filter(language__code=language.code)
    if event_translation.exists():
        return event_translation.first().creator
    if all_event_translations.exists():
        event_translation = all_event_translations.first()
        return '{creator} ({language})'.format(
            creator=event_translation.creator,
            language=event_translation.language
        )
    return ''


@register.filter
def event_translation_last_updated(event, language):
    all_event_translations = event.event_translations
    event_translation = all_event_translations.filter(language__code=language.code)
    if event_translation.exists():
        return event_translation.first().last_updated
    if all_event_translations.exists():
        return all_event_translations.first().last_updated
    return ''


@register.filter
def event_translation_created_date(event, language):
    all_event_translations = event.event_translations
    event_translation = all_event_translations.filter(language__code=language.code)
    if event_translation.exists():
        return event_translation.first().created_date
    if all_event_translations.exists():
        return all_event_translations.first().created_date
    return ''
