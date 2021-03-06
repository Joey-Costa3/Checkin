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

def permissionDenied(request):
    return render(request, 'attendance/permissionDenied.html')

#check to see if the semester being passed is current. 
def isSemesterActive(semester):
        s = Semester.objects.filter(id=semester['id'])[0]
        today = datetime.date.today()
        return s.begin_date <= today and today <= s.end_date

#get the semester that it currently is.
def getCurrentSemester():
        today = datetime.date.today()
        semester = Semester.objects.filter(begin_date__lt=today, end_date__gt=today)
        return semester[0]

@login_required
def logout(request):
        messages.info(request, 'You have been logged out sucessfully.')
        return dLogout(request)

#attendance/instructor.html
@login_required
def instructorHome(request, user_id):
        user = get_object_or_404(User, username=user_id)
        if not validateUser(request.user, user=user):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        semester = getCurrentSemester()
        instructor=get_object_or_404(User,username=user_id)
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=instructor.username,semester_id=semester.id).order_by('name')
        for c in c_list:
                 c.semester_id= Semester.objects.filter(id=c.semester_id)[0]
        c_list_old = Course.objects.filter(isactive=True).filter(instructorusername=instructor.username).exclude(semester_id=semester.id).order_by('name', '-semester_id')
        for c in c_list_old:
                 c.semester_id= Semester.objects.filter(id=c.semester_id)[0]

        if len(c_list) == 0:
            messages.error(request, "You are not an instructor for any courses")
            return redirect('permissionDeniedURL')

        return render(request, 'attendance/instructor.html', {'instructor': instructor, 'courses': c_list, 'semester':semester, 'old_courses':c_list_old})

#attendance/course.html
@login_required
def courseHome(request,semester_id, course_id):

        semesterForGivenID = Semester.objects.filter(name=semester_id).values('id')[0]
        course = get_object_or_404(Course, name=course_id, semester_id=semesterForGivenID['id'])
        if not validateUser(request.user, user=request.user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        semester = Semester.objects.get(id=semesterForGivenID['id'])

        inProgress=None;
        c = "11111"
        DIGITS = '123456789'
        endtime = date.today()
        # generate attendance records for added day
        if request.method == 'POST':
                form=CourseHome(request.POST)
                if form.is_valid():
                        saved=form.cleaned_data
                        coursecode = CourseCode.objects.filter(codedate=date.today()).filter(courseid=course.id)
                        print(coursecode.count())
                        if coursecode.count() is 0:
                                for s in course.student_list.all():
                                        AttendanceRecord.objects.create(courseid=course.id,user=s,studentusername=s.username,date=date.today())
                                #create course code for added day with given time
                                c=''.join(random.choice(string.ascii_uppercase + DIGITS) for _ in range(5))

                                matches=1
                                while matches != 0:
                                        while CourseCode.objects.filter(code=c).count() > 0:
                                                 c=''.join(random.choice(string.ascii_uppercase + DIGITS) for _ in range(5))
                                        d=datetime.datetime.now() + datetime.timedelta(0,0,0,0,int(saved['time']))

                                        f=CourseCode.objects.filter(code=c, codedate=date.today())
                                        matches=f.count()

                                CourseCode.objects.create(code=c,courseid=course.id,expirationtime=d).save()
                                
                                return redirect('courseHomeURL',
                                         semester_id=semester.name, course_id=course_id
                                )
                        else:
                                #messages.info(request, 'Attendance in progress with code: ' + coursecode.first().code)
                                c=coursecode.first().code
                                endtime=coursecode.first().expirationtime
                                inProgress=True
                else:
                        messages.info(request, 'INVALID')
        else:
                form = CourseHome(initial = { 'time': course.checkinwindow })
                coursecode = CourseCode.objects.filter(codedate=date.today()).filter(courseid=course.id)
                if coursecode.count() > 0:
                        #messages.info(request, 'Attendance in progress with code: ' + coursecode.first().code)
                        c=coursecode.first().code
                        endtime=coursecode.first().expirationtime
                        inProgress=True
                        # don't need to pass a message
                #else:

                        #messages.info(request, 'Attendance not yet started for today')
        student_list = [[]]
        for s in course.student_list.all().values():
                student_list.append(s)
        student_list.pop(0)
        d_list=AttendanceRecord.objects.filter(courseid=course.id).values('date').distinct().order_by('-date')
        instructor=get_object_or_404(User,username=request.user.username)
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=instructor.username).order_by('name')
        # with the dates we will then get all attendance records for each user. These for loops are for formatting the CSV file for a class
        for a in d_list:
                a['usernames']=AttendanceRecord.objects.filter(courseid=course.id).values('studentusername').distinct().order_by('studentusername')
        for a in d_list:
                for s in a['usernames']:
                        f=AttendanceRecord.objects.filter(courseid=course.id,studentusername=s['studentusername'],date=a['date']).values('status')
                        if not f:
                                s['attendance']=""
                        else:
                                s['attendance']=f[0]['status']

        semesterActive = isSemesterActive(semesterForGivenID)

        return render(request, 'attendance/course.html', {'course': course,'attendance':d_list,'code':c, 'instructor': instructor,
            'courses': c_list, 'form':form, 'students': student_list, 'inProgress': inProgress, 'endtime':endtime, 'semester_id':semester, 'active':semesterActive})

#attendance/courseAttendanceByDay.html
@login_required
def attendance(request, semester_id, course_id, day):
        semesterForGivenID = Semester.objects.filter(name=semester_id).values('id')[0]
        course = get_object_or_404(Course, name=course_id, semester_id=semesterForGivenID['id'])
        user = get_object_or_404(User, username=request.user.username)
        semester = Semester.objects.get(id=semesterForGivenID['id'])
        s_list=AttendanceRecord.objects.filter(courseid=course.id).filter(date=day).order_by('studentusername')
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=user.username).order_by('name')
        #print(s_list)

        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)

        if not validateUser(request.user, user=user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        semesterActive = isSemesterActive(semesterForGivenID)

        return render(request, 'attendance/courseAttendanceByDay.html', {'course': course, 'course_id': course_id, 'day': day,'recordList':s_list,
            'instructor': user, 'courses': c_list, 'semester_id':semester, 'active':semesterActive})

#attendance/courseAttendanceByStudent.html
@login_required
def studentAttendance(request, semester_id, course_id, user_id):
        semesterForGivenID = Semester.objects.filter(name=semester_id).values('id')[0]
        course = get_object_or_404(Course, name=course_id, semester_id=semesterForGivenID['id'])
        user = get_object_or_404(User, username=request.user.username)
        a_list=AttendanceRecord.objects.filter(courseid=course.id).filter(studentusername=user_id).order_by('date')
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=user.username).order_by('name')
        semester = Semester.objects.get(id=semesterForGivenID['id'])
        present=sum(a.status == "P" for a in a_list)
        excused=sum(a.status == "E" for a in a_list)
        tardy=sum(a.status == "T" for a in a_list)
        total=len(a_list)
        absent=total-present-excused-tardy

        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)
        student = settings.GET_USER_BY_USERNAME(user_id)
        if not validateUser(request.user, user=user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        return render(request, 'attendance/courseAttendanceByStudent.html', {'course': course, 'course_id': course_id,
            'student': student, 'recordList':a_list, 'instructor': user, 'courses': c_list, 'a': absent, 't': total, 'p': present, 'e':excused,'tardy':tardy, 'semester_id':semester})

#attendance/editAttendance.html
@login_required
def editAttendance(request, semester_id, course_id, day):
        semesterForGivenID = Semester.objects.filter(name=semester_id).values('id')[0]
        course = get_object_or_404(Course, name=course_id, semester_id=semesterForGivenID['id'])
        s_list=AttendanceRecord.objects.filter(courseid=course.id).filter(date=day).order_by('studentusername')
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=request.user.username).order_by('name')
        semester = Semester.objects.get(id=semesterForGivenID['id'])
        RecordFormset=modelformset_factory(AttendanceRecord,form=AttendanceStatus,can_delete=False, extra=0)
        if not validateUser(request.user, user=request.user, course=course):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        #updating attendance after change is submitted by instructor
        if request.method == 'POST':
                formset=RecordFormset(request.POST)
                if formset.is_valid():
                        instances=formset.save(commit=False)
                        messages.info(request, 'UPDATED')
                        for instance in instances:
                                instance.save()
                        return redirect('courseAttendanceURL',
                                semester_id=semester.name,
                                course_id=course_id,
                                day=day,
                        )
                else:
                        messages.info(request, 'INVALID')
        else:
                formset=RecordFormset(queryset=s_list)
        return render(request, 'attendance/editAttendance.html', {'course_id': course_id, 'day': day,'formset':formset, 'instructor': request.user, 'courses': c_list, 'semester_id':semester})

#attendance/courseEdit.html
@login_required
def editCourse(request, semester_id, course_id):
        semesterForGivenID = Semester.objects.filter(name=semester_id).values('id')[0]
        newc = get_object_or_404(Course, name=course_id, semester_id=semesterForGivenID['id'])
        user = get_object_or_404(User, username=request.user.username)
        if not validateUser(request.user, user=user, course=newc):
                messages.error(request, "You do not have permission to view {}".format(request.get_full_path()))
                return redirect('permissionDeniedURL')
        semester = Semester.objects.get(id=semesterForGivenID['id'])

        if request.method == 'POST':
                form = UpdateCourse(request.POST)
                if form.is_valid():
                        saved = form.cleaned_data
                        newc.checkinwindow = saved['checkinwindow']
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
                                semester_id=semester.name, course_id=newc.name
                        )
                else:
                        messages.info(request, 'INVALID')
        else:
                student_list = []
                for s in newc.student_list.all().values('username'):
                        student_list.append(s['username'])
                form = UpdateCourse(initial = {
                        'checkinwindow': newc.checkinwindow,
                        'students': "\n".join(student_list),
                })
        instructor=get_object_or_404(User,username=request.user.username)
        c_list= Course.objects.filter(isactive=True).filter(instructorusername=instructor.username).order_by('name')
        return render(request, 'attendance/courseEdit.html',
                {'course_id': course_id, 'semester_id':semester, 'form': form, 'instructor': instructor, 'courses': c_list, 'course':newc}
        )

#attendance/studentCheckIn.html
@login_required
def studentCheckIn(request):

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
                                messages.error(request, "Course code entered incorrectly. Please go back and try again.")
                                return render(request, 'attendance/studentCheckIn.html', {'form': form})

                        # check for expiration
                        expireTime = codeObj.expirationtime
                        currTime = datetime.datetime.now()
                        if currTime > expireTime:
                                messages.error(request, "This attendance code has expired.")
                                return render(request, 'attendance/studentCheckIn.html', {'form': form})

                        # get course associated w/ code
                        course = codeObj.getCourse()
                        course_id = course.getId()
                        date = expireTime.date()

                        # update attendance record for user in that course
                        try:
                                attObj = AttendanceRecord.objects.get(courseid=course_id,
                                        studentusername=request.user.username,
                                        date=date.today())
                                if attObj.status == 'P':
                                    messages.info(request, 'You have already checked into this course')
                                    return render(request, 'attendance/studentCheckIn.html', {'form': form})
                                attObj.status = 'P'
                                attObj.signin = currTime
                        except ObjectDoesNotExist:
                                # add student to the course and mark them as present for today
                                student = settings.GET_USER_BY_USERNAME(request.user.username)
                                course.student_list.add(student)
                                AttendanceRecord.objects.create(courseid=course_id,user=student,studentusername=student.username,date=date.today(),status='P',signin=currTime)
                                # check to see if they missed the first x classes and mark them as unexcused for those days
                                records = CourseCode.objects.filter(courseid=course_id).exclude(codedate=date.today()).order_by('codedate')
                                for r in records:
                                    AttendanceRecord.objects.create(courseid=course_id,user=student,studentusername=student.username,date=r.codedate,status='U')
                                messages.success(request, 'Your attendance has been recorded for ' + course.display_name + ' on ' + datetime.date.today().strftime("%d-%m-%y"))
                                return render(request, 'attendance/studentCheckIn.html', {'form': form})

                        attObj.save()
                        messages.success(request, 'Your attendance has been recorded for ' + course.display_name + ' on ' + datetime.date.today().strftime("%d-%m-%y"))
                        return render(request, 'attendance/studentCheckIn.html', {'form': form})

        # display the form and also display the students attendance records
        else:
                form = CodeEntryForm()

        # pass back this list before rendering page. Display info in html
        return render(request, 'attendance/studentCheckIn.html', {'form': form})

#attendance/studentViewAttendance.html
@login_required
def studentViewAttendance(request):
        # get every attendance record for our student they will only be able to see the current semesters records
        semester = getCurrentSemester()
        activeCourses = Course.objects.filter(semester_id=semester.id)
        c_id = []
        for ac in activeCourses:
                  c_id.append(ac.id)
        student_records = AttendanceRecord.objects.filter(studentusername=request.user.username,courseid__in=c_id).order_by('courseid', '-date')

        # change the 'courseid' field to actually grab the course display name
        for r in student_records:
                r.courseid = Course.objects.get(pk=r.courseid).name;
        # get the values separated by course. This way we will be able to display data separated by course
        records = [[]]
        if student_records.count() > 0:
                course_id = student_records[0].courseid
                entry = 0
                for r in student_records:
                        if course_id == r.courseid:
                                records[entry].append(r)
                        else:
                                records.append([])
                                entry += 1
                                records[entry].append(r)
                                course_id = r.courseid
                
        # pass back this list before rendering page. Display info in html
        return render(request, 'attendance/studentViewAttendance.html', {'records': student_records, 'username': request.user.username, 'course_records':records})
