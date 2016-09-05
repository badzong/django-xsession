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

    # Build domain list, with support for subdomains
    domains = copy.copy(settings.XSESSION_DOMAINS)
    for domain in settings.XSESSION_DOMAINS:
        if host.endswith(domain):
            domains.remove(domain)

    render_context = {
        'path': getattr(settings, 'XSESSION_FILENAME', 'xsession_loader.js'),
        'domains': domains,
        'port': str(request.META['SERVER_PORT']),  # if port 8080, 8000 and etc
    }

    return render_context
