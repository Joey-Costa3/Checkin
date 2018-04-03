from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from optparse import make_option
from attendance_tracker import settings
from ...models import Semester, Course

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('semester_name')
    parser.add_argument('name')
    parser.add_argument(
      '--display-name',
      action='store',
      dest='display',
      help='Specify the display name (defaults to course name)',
    ),
    parser.add_argument(
      '--instructor',
      action='append',
      help='Add an instructor to the course',
    ),

  def handle(self, *args, **options):
    semester_name = options['semester_name']
    name = options['name']
    display_name = options['display'] or name
    semester = Semester.objects.get(name=semester_name)
    for username in options['instructor'] or []:
      user = settings.GET_USER_BY_USERNAME(username)
    course = Course(
      semester=semester,
      name=name,
      display_name=display_name,
      instructor=user,
      instructorusername=user,
    )
    try:
      course.full_clean()
    except ValidationError as  e:
      msg = 'Validation failed for the following reasons:\n- ' \
         + '\n- '.join(e.messages)
      raise CommandError(msg)
    course.save()
