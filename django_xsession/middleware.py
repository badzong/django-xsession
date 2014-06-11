# coding=utf-8
from django.conf import settings
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
        loader_path = getattr(settings, 'XSESSION_FILENAME', 'xsession_loader.js')
        if path != loader_path:
            return

        if not request.session.keys() and not request.user.is_authenticated():
            return HttpResponse('', mimetype="text/javascript")

        # Get session cookie
        cookie = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
        sessionid = request.COOKIES[cookie]

        # Default age (see Django docs)
        age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)
        expire = int(time.time()) + age
        utc = datetime.datetime.utcfromtimestamp(expire)

        # Got session. Set sessionid and reload
        if settings.SESSION_COOKIE_HTTPONLY:
            javascript = "document.cookie='%s=%s; expires=%s'; document.cookie='set_httponly=1; expires=%s'; window.location.reload();" % (cookie, sessionid, utc, utc)
        else:
            javascript = "document.cookie='%s=%s; expires=%s'; window.location.reload();" % (cookie, sessionid, utc)

        return HttpResponse(javascript, mimetype="text/javascript")

    def process_response(self, request, response):
        # Clear out expired session cookies.  We need to do this because, by default, our Django session
        # cookies are set with httpOnly, meaning we can't clear them using our JS shim here.
        cookie = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
        if request.COOKIES.get(cookie) and not (request.session.keys() or request.user.is_authenticated()):
            response.delete_cookie(cookie, domain=getattr(settings, 'SESSION_COOKIE_DOMAIN', ''))
        else:
            # If we just got a session cookie via our JS shim, we should re-add the cookie as httpOnly
            if request.COOKIES.get('set_httponly'):
                response.delete_cookie('set_httponly')
                age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)
                response.set_cookie(
                    cookie,
                    value=request.COOKIES[cookie],
                    expires=age,
                    domain=getattr(settings, 'SESSION_COOKIE_DOMAIN'),
                    secure=getattr(settings, 'SESSION_COOKIE_SECURE'),
                    httponly=True,
                )

        return response
