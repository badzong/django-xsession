# coding=utf-8
import settings
from django.http import HttpResponse
import time, datetime

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
        if path != settings.__dict__.get('XSESSION_FILENAME','xsession_loader.js'):
            return

        # Get session cookie
        cookie = settings.__dict__.get('SESSION_COOKIE_NAME', 'sessionid')
        try:
            sessionid = request.COOKIES[cookie]
        except KeyError:
            return HttpResponse('', mimetype="text/javascript")

        # Default age (see Django docs)
        age = settings.__dict__.get('SESSION_COOKIE_AGE', 1209600)
        expire = int(time.time()) + age
        utc = datetime.datetime.utcfromtimestamp(expire)

        # Got session. Set sessionid and reload
        javascript = "document.cookie='%s=%s; expires=%s'; window.location.reload();" % (cookie, sessionid, utc)

        return HttpResponse(javascript, mimetype="text/javascript")
