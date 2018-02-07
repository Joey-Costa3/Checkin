from .models import User, Course
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist

##
## Arguments: specify either user or course, not both
##
##
def validateUser(loggedInUser, **kwargs):
	try:
		user = kwargs['user']
	except:
		user = None
	try:
		course = kwargs['course']
	except:
		course = None

	if not loggedInUser.is_authenticated:
		return False

	if user is not None and course is None:
		if user.username == loggedInUser.username:
			return True
	if course is not None and user is None:
		if loggedInUser.username == course.instructorUsername:
			return True
	if course is not None and user is not None:
		if (loggedInUser.username == course.instructorUsername and loggedInUser.username == user.username):
			return True
	return False

def addNewUser(newUsername):

	if not User.objects.get(username=newUsername):
		user = User.objects.create_user(newUsername, 'dummy@dummy.com', 'password')
		user.save()
