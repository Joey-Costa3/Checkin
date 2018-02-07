from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as userLogin
from django.contrib.auth.views import logout_then_login as dLogout
from django.forms import modelformset_factory
from attendance_tracker import settings
import datetime
from datetime import date
import random
import string

from .models import *
from .forms import *

from .helpers import validateUser

@login_required
def logout(request):
        messages.info(request, 'You have been logged out sucessfully.')
        return dLogout(request)

@login_required
def instructorHome(request, user_id):
        user = get_object_or_404(User, username=user_id)
        if not validateUser(request.user, user=user):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')

        instructor=get_object_or_404(User,username=user_id)
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=instructor.username).order_by('name')
        return render(request, 'attendance/instructor.html', {'instructor': instructor, 'courses': c_list})

@login_required
def courseHome(request, course_id):
        course = get_object_or_404(Course, name=course_id)        
        if not validateUser(request.user, user=request.user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')
        
        c = "11111"
        DIGITS = '123456789'
        # generate attendance records for added day
        if request.method == 'POST':
                form=CourseHome(request.POST)
                if form.is_valid():
                        saved=form.cleaned_data
                        courseCode = CourseCode.objects.filter(codeDate=date.today()).filter(courseId=course.id)
                        print(courseCode.count())
                        if courseCode.count() is 0:
                                for s in course.student_list.all():
                                        AttendanceRecord.objects.create(CourseId=course.id,user=s,studentUsername=s.username,date=date.today())
                                #create course code for added day with given time

                                c=''.join(random.choice(string.ascii_uppercase + DIGITS) for _ in range(5))
                                while CourseCode.objects.filter(code=c).count() > 0:
                                        c=''.join(random.choice(string.ascii_uppercase + DIGITS) for _ in range(5))
                                d=datetime.datetime.now() + datetime.timedelta(0,0,0,0,int(saved['time']))
                                CourseCode.objects.create(code=c,courseId=course.id,expirationTime=d).save()
                                return redirect('courseHome',
                                        course_id=course_id,
                                )
                        else:
                                messages.info(request, 'Attendance in progress: <span id="codeBlock">' + courseCode.first().code + '</span>', extra_tags='safe')
                else:
                        messages.info(request, 'INVALID')
        else:
                form = CourseHome(initial = { 'time': course.checkinWindow })
                courseCode = CourseCode.objects.filter(codeDate=date.today()).filter(courseId=course.id)
                if courseCode.count() > 0:
                        messages.info(request, 'Attendance in progress: <span id="codeBlock">' + courseCode.first().code + '</span>', extra_tags='safe')
                else:
                        messages.info(request, 'Attendance not yet started for today')
        student_list = []
        for s in course.student_list.all().values('username'):
                student_list.append(s['username'])
        d_list=AttendanceRecord.objects.filter(CourseId=course.id).values('date').distinct().order_by('-date')
        instructor=get_object_or_404(User,username=request.user.username)
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=instructor.username).order_by('name')
        return render(request, 'attendance/course.html', {'course': course,'attendance':d_list,'code':c, 'instructor': instructor, 'courses': c_list, 'form':form, 'students': student_list})

@login_required
def attendance(request, course_id, day):
        course = get_object_or_404(Course, name=course_id)
        user = get_object_or_404(User, username=request.user.username)
        s_list=AttendanceRecord.objects.filter(CourseId=course.id).filter(date=day).order_by('studentUsername')
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=user.username).order_by('name')
        print(s_list)

        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)

        if not validateUser(request.user, user=user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')
        return render(request, 'attendance/attendance.html', {'course_id': course_id, 'day': day,'recordList':s_list, 'instructor': user, 'courses': c_list})

@login_required
def studentAttendance(request, course_id, user_id):
        course = get_object_or_404(Course, name=course_id)
        user = get_object_or_404(User, username=request.user.username)
        a_list=AttendanceRecord.objects.filter(CourseId=course.id).filter(studentUsername=user_id).order_by('date')
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=user.username).order_by('name')

        present=sum(a.status == "P" for a in a_list)
        total=len(a_list)
        absent=total-present

        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)

        if not validateUser(request.user, user=user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')
        return render(request, 'attendance/studentAttendance.html', {'course_id': course_id, 'student': user_id, 'recordList':a_list, 'instructor': user, 'courses': c_list, 'a': absent, 't': total})
@login_required

def editAttendance(request, user_id, course_id, day):
        course = get_object_or_404(Course, name=course_id)
        user = get_object_or_404(User, username=user_id)
        s_list=AttendanceRecord.objects.filter(CourseId=course.id).filter(date=day).order_by('studentUsername')
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=user.username).order_by('name')

        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)

        if not validateUser(request.user, user=user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')
        #updating atttendance after change is submitted by instructor
        if request.method == 'POST':
                formset=RecordFormset(request.POST)
                if formset.is_valid():
                        instances=formset.save(commit=False)
                        messages.info(request, 'UPDATED')
                        for instance in instances:
                                instance.save()
                        return redirect('courseAttendanceURL',
                                user_id=user_id,
                                course_id=course_id,
                                day=day,
                        )
                else:
                        messages.info(request, 'INVALID')
        else:
                formset=RecordFormset(queryset=s_list)
        return render(request, 'attendance/editAttendance.html', {'user_id':user_id,'course_id': course_id, 'day': day,'formset':formset, 'instructor': user, 'courses': c_list})

@login_required
def editCourse(request, course_id):
        newc = get_object_or_404(Course, name=course_id)
        user = get_object_or_404(User, username=request.user.username)
        if not validateUser(request.user, user=user, course=newc):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('loginURL')
        
        if request.method == 'POST':
                form = UpdateCourse(request.POST)
                if form.is_valid():
                        saved = form.cleaned_data
                        newc.checkinWindow = saved['checkinWindow']
                        newc.student_list.clear()
                        newc.save()
                        for s in saved['students'].strip().split("\r\n"):
                                if len(s) > 0:
					for t in s.split(";"):
                                        	try:
                                        	        student = settings.GET_USER_BY_USERNAME(t)
                                        	        newc.student_list.add(student)
                                        	except User.DoesNotExist as e:
                                        	        raise Exception('User not found: ' + t)
                        messages.info(request, 'UPDATED')
                        return redirect('editCourseURL',
                                course_id=newc.name,
                        )
                else:
                        messages.info(request, 'INVALID')
        else:
                student_list = []
                for s in newc.student_list.all().values('username'):
                        student_list.append(s['username'])
                form = UpdateCourse(initial = {
                        'checkinWindow': newc.checkinWindow,
                        'students': "\n".join(student_list),
                })
        instructor=get_object_or_404(User,username=request.user.username)
        c_list= Course.objects.filter(isActive=True).filter(instructorUsername=instructor.username).order_by('name')
        return render(request, 'attendance/editCourse.html',
                {'course_id': course_id, 'form': form, 'instructor': instructor, 'courses': c_list}
        )

@login_required
def studentSignIn(request):

        # we're processing a code entry
        if request.method == 'POST':

                form = CodeEntryForm(request.POST)
                if form.is_valid():

                        # get code from user input
                        newCode = request.POST['code']

                        # find code object in database matching user code
                        try:
                                codeObj = CourseCode.objects.get(code=newCode)
                        except ObjectDoesNotExist:
                                return render(request, 'attendance/failure.html')

                        # check for expiration
                        expireTime = codeObj.expirationTime
                        currTime = datetime.datetime.now()
                        if currTime > expireTime:
                                return render(request, 'attendance/codeExpiredFailure.html')

                        # get course associated w/ code
                        course = codeObj.getCourse()
                        course_id = course.getId()
                        date = expireTime.date()

                        # update attendance record for user in that course
                        try:
                                attObj = AttendanceRecord.objects.get(CourseId=course_id, 
                                        studentUsername=request.user.username,
                                        date=date)
                                attObj.status = 'P'
                                attObj.signIn = currTime
                        except ObjectDoesNotExist:
                                return render(request, 'attendance/noMatchingAttRecordFailure.html')

                        attObj.save()
                        return render(request, 'attendance/success.html')

        # we're not processing a code entry so just have to define the form to display
        else:
                form = CodeEntryForm()

        return render(request, 'attendance/studentSignIn.html', {'form': form})