import copy
import settings
from django import template

register = template.Library()

@register.inclusion_tag('sso.html', takes_context=True)
def sso_request(context):

    try:
        request = context['request']
    except KeyError:
        return {}

    # User is already authenticated
    if request.user.is_authenticated():
        return {}

    try:
        host = request.META['HTTP_HOST']
    except KeyError:
        return {}

    domains = copy.copy(settings.SSO_DOMAINS)
    try:
        domains.remove(host)
    except ValueError:
        pass

    render_context = {
        'sso_path': settings.SSO_FILENAME,
        'domains': domains,
    }

    return render_context
