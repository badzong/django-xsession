django_xsession
===============

django_xsession is a middleware that offers session sharing across multiple
domains (using the same session backend obviously). Can be used to allow
single sign-on across multiple websites.



Install
-------

    python setup.py install


Usage
-----

Add django_xsession to your INSTALLED_APPS and load the XSessionMiddleware
class. Then set the domain names you want to share the session cookie.

settings.py snippet:

```python
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_xsession.middleware.XSessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_xsession',
)

XSESSION_DOMAINS = ['www.domain1.org', 'www.domain2.org', 'www.domain3.org']
```

You also need to add the xsession_loader to the head section of your base
template.

base.html (or whatever filename you use):

```html
{% load django_xsession %}
<html>
    <head>
        {% xsession_loader %}
    </head>
    <body>
        <h1>hello world</h1>
    </body>
</html>
```

You'll need to make sure that you're rendering the template with `RequestContext`, as well.
