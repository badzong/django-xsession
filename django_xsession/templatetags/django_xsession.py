import copy
from django.conf import settings
from django import template

register = template.Library()

@register.inclusion_tag('django_xsession/loader.html', takes_context=True)
def xsession_loader(context):

    try:
        request = context['request']
    except KeyError:
        return {}

    # Check if XSessionMiddleware was loaded
    if not hasattr(request, 'xsession'):
        return {}

    if request.session.keys() or request.user.is_authenticated():
        return {}

    cookie = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
    if request.COOKIES.get(cookie, None):
        return {}

    # No session found
    try:
        host = request.META['HTTP_HOST']
    except KeyError:
        return {}

    # Build domain list
    domains = copy.copy(settings.XSESSION_DOMAINS)
    try:
        domains.remove(host)
    except ValueError:
        pass

    render_context = {
        'path': getattr(settings, 'XSESSION_FILENAME', 'xsession_loader.js'),
        'domains': domains,
    }

    return render_context
