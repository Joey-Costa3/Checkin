from django.db import models
from django.contrib.auth.models import User
import re

name_re = re.compile(r'[a-zA-Z0-9](?:[a-zA-Z0-9_-]*[a-zA-Z0-9])?$')

# GENERAL COMMENTS: will be written into readme... eventually.
#
# Sometimes django will get confused and refuse to make migrations. If
# this happens, you must do the following:
# 1. enter psql terminal, run: delete from django_migrations where app='attendance';
# 2. rm attendance/migrations/0*.py
# 3. ./manage.py makemigrations; ./manage migrate
#
# ProgrammingError: relation "<whatever>" already exists
# sometimes this will happen when you attempt a migration. In this case, do
# ./manage.py migrate --fake attendance

class Semester(models.Model):
  name = models.CharField(max_length=20, unique=True)
  display_name = models.CharField(max_length=20, unique=True, blank=True)
  begin_date = models.DateField()
  end_date = models.DateField()

  class Meta:
    ordering = ['-begin_date', 'end_date']

  def __unicode__(self):
    return self.name

  #def get_absolute_url(self):
  #  return reverse('webhandin.handin.views.semester_course_list',
  #                 args=[self.name])

  def clean_fields(self, exclude=None):
    err = {}
    if not exclude or 'name' not in exclude:
      if len(self.name) > Semester._meta.get_field('name').max_length:
        err.setdefault('name', []).append('Semester name is too long')
      if not name_re.match(self.name):
        err.setdefault('name', []).append('Semester name must be alphanumeric')
    if not exclude or 'display_name' not in exclude:
      max_length = Semester._meta.get_field('display_name').max_length
      if len(self.display_name) > max_length:
        err.setdefault('display_name', []).append('Semester display name is '
                                                  'too long')
    if err:
      raise ValidationError(err)

  def clean(self):
    messages = []
    if not self.display_name:
      self.display_name = self.name
    if self.begin_date > self.end_date:
      messages.append('Semester begins before it ends')
    if messages:
      raise ValidationError(messages)

  def is_in_session(self):
    today = datetime.date.today()
    return self.begin_date <= today and today <= self.end_date

class Course(models.Model):
	semester = models.ForeignKey(Semester, db_index=True)
	name = models.CharField(null=True, max_length=20)
	display_name = models.CharField(max_length=20, blank=True)
	instructor = models.CharField(max_length=20, blank=True)
	student_list = models.ManyToManyField(User, blank=True, related_name='+')
	instructorUsername = models.CharField(max_length=15, default="")
	checkinWindow = models.PositiveSmallIntegerField(default=10)
	isActive = models.BooleanField(default=True)

	def getId(self):
		return self.id

	def getInstructor(self):
		return User.objects.get(username=self.instructorUsername)

	def isInstructor(self,instruct):
		if self.instructorUsername==instruct.username:
			return True
		else:
			return False

	def __str__(self):
		return "Instructor: {}, Students:\n{}".format(self.getInstructor(), self.student_list.all())

class CourseCode(models.Model):
	code = models.CharField(null=False, max_length=5)
	courseId = models.IntegerField(default=0)
	codeDate = models.DateField(auto_now_add = True)
	expirationTime = models.DateTimeField()

	def getCourse(self):
		return Course.objects.get(id=self.courseId)

	def __str__(self):
		return "{}, code = {}, expiration = {}".format(self.getCourse(), self.code, self.expirationTime)

class AttendanceRecord(models.Model):
	user = models.ForeignKey(User)
	CourseId = models.IntegerField(null=True)
	studentUsername = models.CharField(max_length=10, default="")
	date = models.DateField()
	signIn = models.DateTimeField(blank=True, null=True)

	PRESENT = 'P'
	EXCUSED = 'E'
	UNEXCUSED = 'U'
	STATUS_CHOICES = (
		(PRESENT, 'Present'),
		(EXCUSED, 'Escused'),
		(UNEXCUSED, 'Unexcused'),
	)

	status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=UNEXCUSED)

	def getCourse(self):
		return Course.objects.get(id=self.CourseId)

	def getStudent(self):
		return User.objects.get(username=self.studentUsername)

	def __str__(self):
		return "{}, {}, {}, {}".format(self.getCourse(), self.getStudent(), self.date, self.signIn, self.status)
