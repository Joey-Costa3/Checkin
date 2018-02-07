from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import HttpResponse


class AutoLogout:
	def process_view(self, request, view, args, kwargs):
		if not request.user.is_authenticated():
			return

		try:
			if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
			auth.logout(request)
			del request.session['last_touch']

			messages.info(request, "You have been Logged out")
			return HttpResponse('GoodJob Bub')
		except KeyError:
			pass

		request.session['last_touch'] = datetime.now()

	def process_response(request, response):
		return response
