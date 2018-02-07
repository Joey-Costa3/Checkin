from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

course_prefix = r'course/(?P<course_id>[a-zA-Z0-9\-]{,20})/'
instructor_prefix = r'instructor/(?P<user_id>[a-zA-Z0-9]{,15})/'

urlpatterns = [
	url(course_prefix + r'home/', views.courseHome, name='courseHome'),
	url(course_prefix + r'editcourse/$',
		views.editCourse,
		name='editCourseURL'),
	url(r'^student/signin/', views.studentSignIn, name='studentSignInURL'),
	url(course_prefix + r'attendance/(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
		views.attendance,
		name='courseAttendanceURL'),
	url(course_prefix + r'attendance/student/(?P<user_id>[a-zA-Z0-9]{,15})/$',
		views.studentAttendance,
		name='courseStudentAttendanceURL'),
	url(course_prefix + r'attendance/edit/(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
		views.editAttendance,
		name='editAttendanceURL'),
	url(instructor_prefix + r'home/', views.instructorHome, name='instructorURL'),
	url(r'login/', auth_views.login, {'template_name': 'attendance/login.html'}, name='loginURL'),
	url(r'logout/', auth_views.logout, {'next_page': '/'}, name='logoutURL'),
	url(r'^$', RedirectView.as_view(pattern_name='loginURL', permanent=False)),
]
