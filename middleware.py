# coding=utf-8
import settings
from django.http import HttpResponse


class XSessionMiddleware(object):

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

        # Set XSession
        request.xsession = True

        # Skip regular requests
        if path != settings.XSESSION_FILENAME:
            return

        # Get session cookie
        cookie = settings.__dict__.get('SESSION_COOKIE_NAME', 'sessionid')
        try:
            sessionid = request.COOKIES[cookie]
        except KeyError:
            return HttpResponse('', mimetype="text/javascript")

        # Got session. Set sessionid and reload
        javascript = "document.cookie='%s=%s'; window.location.reload();" % (cookie, sessionid)

        return HttpResponse(javascript, mimetype="text/javascript")
