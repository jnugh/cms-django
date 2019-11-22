from django import template

from ..models import Language

register = template.Library()


@register.simple_tag
def get_translation(instance, language_code):
    return instance.translations.filter(language__code=language_code).first()


@register.simple_tag
def translated_language_name(language_code):
    return Language.objects.get(code=language_code).translated_name


# Unify the language codes of backend and content languages
@register.simple_tag
def unify_language_code(language_code):
    if language_code == 'en-us':
        return 'en-gb'
    return language_code
