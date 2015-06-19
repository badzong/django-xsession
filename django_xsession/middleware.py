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

        if not hasattr(request, 'session') and not hasattr(request, 'user'):
            # Not far enough along in the django request cycle, so this is likely
            # a middleware response. Let's just return and do nothing here.
            return HttpResponse('', content_type="text/javascript")

        if not (hasattr(request, 'session') and request.session.keys()) and not (hasattr(request, 'user') and request.user.is_authenticated()):
            return HttpResponse('', content_type="text/javascript")

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

        return HttpResponse(javascript, content_type="text/javascript")

    def process_response(self, request, response):
        # Clear out expired session cookies.  We need to do this because, by default, our Django session
        # cookies are set with httpOnly, meaning we can't clear them using our JS shim here.
        cookie = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
        if not hasattr(request, 'session') and not hasattr(request, 'user'):
            # Not far enough along in the django request cycle, so this is likely
            # a middleware response. Let's just return and do nothing here.
            return response
 
        has_session_or_auth = (
            (hasattr(request, 'session') and request.session.keys()) or
            (hasattr(request, 'user') and request.user.is_authenticated())
        )
        if request.COOKIES.get(cookie) and not has_session_or_auth:
            hostname = request.META.get('HTTP_HOST', '').split(':')[0]
            session_domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', '')
            if session_domain.endswith(hostname):
                response.delete_cookie(cookie, domain=session_domain)
            else:
                response.delete_cookie(cookie, domain='')
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
