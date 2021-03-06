from django.http import HttpResponseForbidden
from closedverse import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from re import compile

# Taken from https://python-programming.com/recipes/django-require-authentication-pages/
if settings.force_login:
	EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
	if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
		EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class ClosedMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		# Force logins if it's set
		if settings.force_login and not request.user.is_authenticated:
			if not any(m.match(request.path_info.lstrip('/')) for m in EXEMPT_URLS):
				if request.is_ajax():
					return HttpResponseForbidden("Login is required")
				return redirect(settings.LOGIN_REDIRECT_URL)
		# Fix this ; put something in settings signifying if the server supports HTTPS or not
		if not request.is_secure() and (not settings.DEBUG) and settings.PROD:
			# Let's try to redirect to HTTPS for non-Nintendo stuff.
			if not request.META.get('HTTP_USER_AGENT'):
				return HttpResponseForbidden("You need a user agent.", content_type='text/plain')
			if not request.is_secure() and not 'Nintendo' in request.META['HTTP_USER_AGENT']:
				return redirect('https://{0}{1}'.format(request.get_host(), request.get_full_path()))
		if request.user.is_authenticated:
			""" User active; this doesn't work at the moment due to Postgres not being able to change bools to ints
			if request.user.is_active() == 0:
				return HttpResponseForbidden()
			elif request.user.is_active() == 2:
				return redirect(settings.inactive_redirect)
			"""
			if not request.user.is_active() :
				return HttpResponseForbidden()
			# If there isn't a request.session
			if not request.session.get('passwd'):
				request.session['passwd'] = request.user.password
			else:
				if request.session['passwd'] != request.user.password:
					logout(request)
		response = self.get_response(request)

		return response

"""
return HttpResponseForbidden("Forbidden.", content_type='text/plain')
"""