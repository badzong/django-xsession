# coding=utf-8
import settings
from django.http import HttpResponse


class SSOMiddleware(object):

    def process_request(self, request):

        if 'REQUEST_URI' in request.META:
            uri_key = 'REQUEST_URI'
        elif 'RAW_URI' in request.META:
            uri_key = 'RAW_URI'
        elif 'PATH_INFO' in request.META:
            uri_key = 'PATH_INFO'

        path = request.META[uri_key]

        if path[0] == '/':
            path = path[1:]

        # Regular request
        if path != settings.SSO_FILENAME:
            return

        # SSO_FILENAME requested
        try:
            user = request.user
        except AttributeError:
            return HttpResponse('', mimetype="text/javascript")

        if not user.is_authenticated():
            return HttpResponse('', mimetype="text/javascript")

        cookie = settings.__dict__.get('SESSION_COOKIE_NAME', 'sessionid')

        try:
            sessionid = request.COOKIES[cookie]
        except KeyError:
            return HttpResponse('', mimetype="text/javascript")

        javascript = "document.cookie='%s=%s'; window.location.reload();" % (cookie, sessionid)

        return HttpResponse(javascript, mimetype="text/javascript")
